from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List, Tuple

from shared.schemas.chat import ChatMessage


@dataclass
class Conversation:
    user_key: str
    conversation_id: str
    messages: List[ChatMessage]
    updated_at: datetime


class InMemoryConversationStore:
    def __init__(self, ttl_seconds: int = 0) -> None:
        self._conversations: Dict[Tuple[str, str], Conversation] = {}
        self._lock = asyncio.Lock()
        self._ttl_seconds = ttl_seconds

    async def get(self, user_key: str, conversation_id: str) -> Conversation | None:
        async with self._lock:
            self._evict_expired()
            return self._conversations.get((user_key, conversation_id))

    async def upsert(self, user_key: str, conversation_id: str, messages: List[ChatMessage]) -> Conversation:
        async with self._lock:
            self._evict_expired()
            conversation = Conversation(
                user_key=user_key,
                conversation_id=conversation_id,
                messages=list(messages),
                updated_at=datetime.utcnow(),
            )
            self._conversations[(user_key, conversation_id)] = conversation
            return conversation

    def _evict_expired(self) -> None:
        if self._ttl_seconds <= 0:
            return
        cutoff = datetime.utcnow() - timedelta(seconds=self._ttl_seconds)
        stale_keys = [key for key, convo in self._conversations.items() if convo.updated_at < cutoff]
        for key in stale_keys:
            self._conversations.pop(key, None)
