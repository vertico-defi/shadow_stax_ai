from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.services.persona_loader import load_default_persona
from app.safety.policy import refusal_message


class ModerationState(str, Enum):
    ALLOW = "ALLOW"
    REFUSE_HARD = "REFUSE_HARD"


@dataclass
class SafetyResult:
    state: ModerationState
    reason: Optional[str] = None
    category: Optional[str] = None
    refusal: Optional[str] = None


_SEXUAL_TERMS = r"(sex|sexual|explicit|nude|porn|intercourse|oral|anal|fetish|blowjob|handjob)"
_MINOR_TERMS_STRICT = r"(child|children|kid|kids|minor|underage|preteen)"
_MINOR_TERMS_AMBIGUOUS = r"(teen|teenager|teen-aged)"
_MINOR_PROXIMITY = 80

# Policy category: Minors + sexual content (hard refuse)
_MINORS_EXPLICIT_PATTERN = rf"\b{_MINOR_TERMS_STRICT}\b.{{0,{_MINOR_PROXIMITY}}}\b{_SEXUAL_TERMS}\b|\b{_SEXUAL_TERMS}\b.{{0,{_MINOR_PROXIMITY}}}\b{_MINOR_TERMS_STRICT}\b"

# Policy category: Ambiguous age + sexual content (redirect)
_AMBIGUOUS_AGE_PATTERN = rf"\b{_MINOR_TERMS_AMBIGUOUS}\b.{{0,{_MINOR_PROXIMITY}}}\b{_SEXUAL_TERMS}\b|\b{_SEXUAL_TERMS}\b.{{0,{_MINOR_PROXIMITY}}}\b{_MINOR_TERMS_AMBIGUOUS}\b"

# Policy category: Coercion/trafficking/non-consensual (hard refuse)
_COERCION_PATTERN = r"\b(trafficking|sex slave|forced|coerced|non[- ]consensual)\b.*\b(sex|sexual)\b"

# Policy category: Sexual violence/exploitation (hard refuse)
_VIOLENCE_PATTERN = r"\b(rape|sexual assault)\b"

_ADULT_AGE_PATTERN = r"\b(18|19|2[0-9]|3[0-9]|4[0-9]|5[0-9]|6[0-9]|7[0-9]|8[0-9]|9[0-9])\b"


def _has_explicit_adult_age(text: str) -> bool:
    lowered = text.lower()
    return re.search(_ADULT_AGE_PATTERN, lowered, re.IGNORECASE) is not None


def _matches_pattern(pattern: str, text: str) -> bool:
    lowered = text.lower()
    return re.search(pattern, lowered, re.IGNORECASE | re.DOTALL) is not None


def _matches_any(patterns: list[str], text: str) -> bool:
    return any(_matches_pattern(pattern, text) for pattern in patterns)


def validate_content(text: str, enabled: bool = True, stage: str = "pre-llm") -> SafetyResult:
    if not enabled:
        return SafetyResult(state=ModerationState.ALLOW, reason="safety_disabled", category=None)

    if _matches_pattern(_MINORS_EXPLICIT_PATTERN, text):
        if not _has_explicit_adult_age(text):
            persona = load_default_persona()
            return SafetyResult(
                state=ModerationState.REFUSE_HARD,
                reason="illegal_or_exploitative_sexual_content",
                category="minors",
                refusal=refusal_message(persona),
            )

    if _matches_pattern(_AMBIGUOUS_AGE_PATTERN, text):
        if not _has_explicit_adult_age(text):
            persona = load_default_persona()
            return SafetyResult(
                state=ModerationState.REFUSE_HARD,
                reason="illegal_or_exploitative_sexual_content",
                category="minors",
                refusal=refusal_message(persona),
            )

    if _matches_pattern(_COERCION_PATTERN, text):
        persona = load_default_persona()
        return SafetyResult(
            state=ModerationState.REFUSE_HARD,
            reason="illegal_or_exploitative_sexual_content",
            category="coercion_or_trafficking",
            refusal=refusal_message(persona),
        )

    if _matches_pattern(_VIOLENCE_PATTERN, text):
        persona = load_default_persona()
        return SafetyResult(
            state=ModerationState.REFUSE_HARD,
            reason="illegal_or_exploitative_sexual_content",
            category="sexual_violence",
            refusal=refusal_message(persona),
        )

    return SafetyResult(state=ModerationState.ALLOW, reason="allowed", category=None)
