from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class SafetyResult:
    allowed: bool
    reason: Optional[str] = None


_ILLEGAL_PATTERNS = [
    r"\b(child|children|kid|kids|minor|underage|teen(?:ager)?|preteen)\b.*\b(sex|sexual|explicit|nude|porn|intercourse)\b",
    r"\b(incest)\b",
    r"\b(trafficking|sex slave|forced|coerced)\b.*\b(sex|sexual)\b",
    r"\b(rape|sexual assault|non[- ]consensual)\b",
    r"\b(bestiality|zoophilia)\b",
]


def _matches_illegal(text: str) -> Optional[str]:
    lowered = text.lower()
    for pattern in _ILLEGAL_PATTERNS:
        if re.search(pattern, lowered, re.IGNORECASE | re.DOTALL):
            return pattern
    return None


def validate_content(text: str, enabled: bool = True) -> SafetyResult:
    if not enabled:
        return SafetyResult(allowed=True)
    matched = _matches_illegal(text)
    if matched:
        return SafetyResult(allowed=False, reason="illegal_or_exploitative_sexual_content")
    return SafetyResult(allowed=True)
