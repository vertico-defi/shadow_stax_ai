from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
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
