from __future__ import annotations

import json
from typing import AsyncGenerator, List
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.db.sqlite import (
    create_conversation,
    ensure_relationship_state,
    get_relationship_state,
    get_summary,
    init_db,
    insert_memory,
    insert_message,
    touch_relationship_state,
)
from app.llm.prompt_builder import build_prompt
from app.services.conversation_store import InMemoryConversationStore
from app.services.llm_client import LLMClient
from app.services.memory_extractor import extract_memories
from app.services.rate_limit import SlidingWindowRateLimiter
from app.services.auth import get_user_id_from_authorization
from app.services.safety import ModerationState, validate_content
from shared.config.settings import get_settings
from shared.schemas.chat import ChatMessage, ChatRequest, ChatResponse
from shared.logging.logger import get_logger

router = APIRouter()
settings = get_settings()
logger = get_logger("chatbot-chat")

llm_client = LLMClient()
conversation_store = InMemoryConversationStore(settings.conversation_ttl_seconds)
rate_limiter = SlidingWindowRateLimiter(settings.rate_limit_per_minute, settings.rate_limit_burst)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request) -> ChatResponse | StreamingResponse:
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages_required")
    if not settings.llm_model:
        raise HTTPException(status_code=500, detail="llm_model_not_configured")

    auth_user_id = get_user_id_from_authorization(http_request.headers.get("Authorization"))
    if auth_user_id is None:
        raise HTTPException(status_code=401, detail="auth_required")
    user_key = request.user_id or (http_request.client.host if http_request.client else "anonymous")
    if not await rate_limiter.allow(user_key):
        raise HTTPException(status_code=429, detail="rate_limited")

    conversation_id = request.conversation_id or str(uuid4())
    logger.info(
        "chat_request user_key=%s conversation_id=%s stream=%s",
        user_key,
        conversation_id,
        request.stream,
    )

    existing = await conversation_store.get(user_key, conversation_id)
    history: List[ChatMessage] = []
    if existing:
        history.extend(existing.messages)

    history.extend(request.messages)
    latest_user_message = next(
        (message.content for message in reversed(request.messages) if message.role == "user"),
        "",
    )
    safety_input = validate_content(latest_user_message, settings.safety_blocklist_enabled, stage="pre-llm")
    if safety_input.state == ModerationState.REFUSE_HARD:
        logger.info(
            "moderation state=%s category=%s stage=pre-llm",
            safety_input.state,
            safety_input.category,
        )
        raise HTTPException(status_code=400, detail="blocked_input")

    init_db()
    create_conversation(conversation_id, auth_user_id)
    relationship_row = get_relationship_state(conversation_id)
    if relationship_row is None:
        ensure_relationship_state(conversation_id)
        relationship_row = get_relationship_state(conversation_id)

    user_message_id = None
    if latest_user_message:
        user_message_id = insert_message(
            conversation_id=conversation_id,
            role="user",
            content=latest_user_message,
            model_name=None,
            temperature=None,
            safety_state=safety_input.state.value,
        )

    for extracted in extract_memories(latest_user_message):
        insert_memory(
            conversation_id,
            extracted.memory_type,
            extracted.content,
            extracted.importance,
        )

    touch_relationship_state(conversation_id)
    summary = get_summary(conversation_id)

    history_without_latest = list(history)
    for idx in range(len(history_without_latest) - 1, -1, -1):
        if history_without_latest[idx].role == "user":
            history_without_latest.pop(idx)
            break

    prompt_messages = build_prompt(
        history=history_without_latest,
        relationship_state=dict(relationship_row) if relationship_row else {},
        conversation_summary=summary,
        latest_user_message=latest_user_message,
    )

    if request.stream:
        async def event_stream() -> AsyncGenerator[str, None]:
            yield f"event: meta\ndata: {{\"conversation_id\":\"{conversation_id}\"}}\n\n"
            generated = ""
            async for event_type, chunk in llm_client.stream_chat_completions(
                prompt_messages,
                max_tokens=settings.llm_max_tokens_default,
            ):
                if event_type == "delta":
                    generated += chunk
                    safety_output = validate_content(
                        generated,
                        settings.safety_blocklist_enabled,
                        stage="post-llm",
                    )
                    if safety_output.state == ModerationState.REFUSE_HARD:
                        logger.info(
                            "moderation state=%s category=%s stage=post-llm",
                            safety_output.state,
                            safety_output.category,
                        )
                        refusal_text = safety_output.refusal or "I can't help with that."
                        payload = json.dumps({"error": "blocked_output", "message": refusal_text})
                        yield f"event: blocked\ndata: {payload}\n\n"
                        return
                    yield f"data: {chunk}\n\n"
                elif event_type == "done":
                    break

            assistant_message_id = insert_message(
                conversation_id=conversation_id,
                role="assistant",
                content=generated,
                model_name=settings.llm_model,
                temperature=0.8,
                safety_state=ModerationState.ALLOW.value,
            )
            assistant_message = ChatMessage(role="assistant", content=generated, id=assistant_message_id)
            await conversation_store.upsert(user_key, conversation_id, history + [assistant_message])
            yield "event: done\ndata: [DONE]\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    response_payload = await llm_client.chat_completions(
        prompt_messages,
        max_tokens=settings.llm_max_tokens_default,
    )
    content = (
        response_payload.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )

    safety_output = validate_content(content, settings.safety_blocklist_enabled, stage="post-llm")
    if safety_output.state == ModerationState.REFUSE_HARD:
        logger.info(
            "moderation state=%s category=%s stage=post-llm",
            safety_output.state,
            safety_output.category,
        )
        refusal_text = safety_output.refusal or "I can't help with that."
        assistant_message_id = insert_message(
            conversation_id=conversation_id,
            role="assistant",
            content=refusal_text,
            model_name=settings.llm_model,
            temperature=0.8,
            safety_state=ModerationState.REFUSE_HARD.value,
        )
        assistant_message = ChatMessage(role="assistant", content=refusal_text, id=assistant_message_id)
        await conversation_store.upsert(user_key, conversation_id, history + [assistant_message])
        return ChatResponse(
            conversation_id=conversation_id,
            response=assistant_message,
            status="ok",
            message_id=assistant_message_id,
        )

    assistant_message_id = insert_message(
        conversation_id=conversation_id,
        role="assistant",
        content=content,
        model_name=settings.llm_model,
        temperature=0.8,
        safety_state=ModerationState.ALLOW.value,
    )
    assistant_message = ChatMessage(role="assistant", content=content, id=assistant_message_id)
    await conversation_store.upsert(user_key, conversation_id, history + [assistant_message])
    return ChatResponse(
        conversation_id=conversation_id,
        response=assistant_message,
        status="ok",
        message_id=assistant_message_id,
    )
