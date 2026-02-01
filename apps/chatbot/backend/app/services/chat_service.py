from shared.logging.logger import get_logger
from shared.schemas.chat import ChatMessage, ChatRequest, ChatResponse
from shared.utils.strings import truncate

logger = get_logger("chatbot-service")

def generate_stub_response(request: ChatRequest) -> ChatResponse:
    logger.info("chat_request role=%s content=%s", request.message.role, truncate(request.message.content))
    content = f"Stub response: {truncate(request.message.content)}"
    return ChatResponse(
        response=ChatMessage(role="assistant", content=content),
        status="ok",
    )
