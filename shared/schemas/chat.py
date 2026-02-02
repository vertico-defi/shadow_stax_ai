from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    id: int | None = None
    role: str = Field(..., examples=["user", "assistant"])
    content: str


class ChatRequest(BaseModel):
    user_id: str | None = None
    conversation_id: str | None = None
    messages: list[ChatMessage]
    stream: bool = False


class ChatResponse(BaseModel):
    conversation_id: str
    response: ChatMessage
    status: str = "ok"
    message_id: int | None = None
