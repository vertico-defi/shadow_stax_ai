from __future__ import annotations

from typing import AsyncGenerator, List
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.services.conversation_store import InMemoryConversationStore
from app.services.llm_client import LLMClient
from app.services.rate_limit import SlidingWindowRateLimiter
from app.services.safety import validate_content
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
    input_text = "\n".join(message.content for message in request.messages if message.content)
    safety_input = validate_content(input_text, settings.safety_blocklist_enabled)
    if not safety_input.allowed:
        raise HTTPException(status_code=400, detail="blocked_input")

    if request.stream:
        async def event_stream() -> AsyncGenerator[str, None]:
            yield f"event: meta\ndata: {{\"conversation_id\":\"{conversation_id}\"}}\n\n"
            generated = ""
            async for event_type, chunk in llm_client.stream_chat_completions(
                history,
                max_tokens=settings.llm_max_tokens_default,
            ):
                if event_type == "delta":
                    generated += chunk
                    safety_output = validate_content(generated, settings.safety_blocklist_enabled)
                    if not safety_output.allowed:
                        yield "event: blocked\ndata: {\"error\":\"blocked_output\"}\n\n"
                        return
                    yield f"data: {chunk}\n\n"
                elif event_type == "done":
                    break

            assistant_message = ChatMessage(role="assistant", content=generated)
            await conversation_store.upsert(user_key, conversation_id, history + [assistant_message])
            yield "event: done\ndata: [DONE]\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    response_payload = await llm_client.chat_completions(
        history,
        max_tokens=settings.llm_max_tokens_default,
    )
    content = (
        response_payload.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )

    safety_output = validate_content(content, settings.safety_blocklist_enabled)
    if not safety_output.allowed:
        raise HTTPException(status_code=400, detail="blocked_output")

    assistant_message = ChatMessage(role="assistant", content=content)
    await conversation_store.upsert(user_key, conversation_id, history + [assistant_message])
    return ChatResponse(conversation_id=conversation_id, response=assistant_message, status="ok")
