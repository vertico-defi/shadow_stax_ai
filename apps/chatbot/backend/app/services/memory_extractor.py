from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class ExtractedMemory:
    memory_type: str
    content: str
    importance: float


_PATTERNS = [
    (re.compile(r"\bmy name is ([a-zA-Z0-9 _'-]{2,40})", re.IGNORECASE), "profile", 0.6),
    (re.compile(r"\bi am ([a-zA-Z0-9 _'-]{2,40})", re.IGNORECASE), "profile", 0.4),
    (re.compile(r"\bi like ([^.!?]{2,80})", re.IGNORECASE), "preference", 0.5),
    (re.compile(r"\bi love ([^.!?]{2,80})", re.IGNORECASE), "preference", 0.7),
    (re.compile(r"\bi hate ([^.!?]{2,80})", re.IGNORECASE), "preference", 0.6),
    (re.compile(r"\bi prefer ([^.!?]{2,80})", re.IGNORECASE), "preference", 0.6),
]


def extract_memories(text: str) -> List[ExtractedMemory]:
    memories: List[ExtractedMemory] = []
    for pattern, memory_type, importance in _PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        value = match.group(1).strip()
        if value:
            memories.append(
                ExtractedMemory(
                    memory_type=memory_type,
                    content=value,
                    importance=importance,
                )
            )
    return memories
