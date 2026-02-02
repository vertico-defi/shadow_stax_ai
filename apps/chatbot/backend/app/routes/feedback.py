from __future__ import annotations

import json
from fastapi import APIRouter, Request

from app.db.sqlite import insert_feedback
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.auth import get_user_id_from_authorization

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
def create_feedback(request_body: FeedbackRequest, request: Request) -> FeedbackResponse:
    user_id = get_user_id_from_authorization(request.headers.get("Authorization"))
    tags_json = json.dumps(request_body.tags) if request_body.tags else None
    insert_feedback(
        message_id=request_body.message_id,
        user_id=user_id,
        rating=request_body.rating,
        tags=tags_json,
        rewrite_text=request_body.rewrite_text,
    )
    return FeedbackResponse()
