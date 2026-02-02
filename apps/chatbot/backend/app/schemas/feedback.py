from pydantic import BaseModel, Field
from typing import List, Optional


class FeedbackRequest(BaseModel):
    message_id: int
    rating: str = Field(..., pattern="^(thumbs_up|thumbs_down)$")
    tags: Optional[List[str]] = None
    rewrite_text: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str = "ok"
