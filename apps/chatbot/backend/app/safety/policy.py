from __future__ import annotations

from typing import Dict


ILLEGAL_CATEGORIES = [
    "sexual content involving minors",
    "coercion, trafficking, or non-consensual sexual scenarios",
    "sexual violence or exploitation",
]


def build_safety_policy(persona: Dict) -> str:
    allowed = persona.get("boundaries", {}).get("allowed", [])
    refuse = persona.get("boundaries", {}).get("refuse", [])
    lines = []
    lines.append("Allowed:")
    lines.extend([f"- {item}" for item in allowed])
    lines.append("Refuse:")
    lines.extend([f"- {item}" for item in refuse])
    lines.append("Never allow:")
    lines.extend([f"- {item}" for item in ILLEGAL_CATEGORIES])
    return "\n".join(lines)


def refusal_message(persona: Dict) -> str:
    templates = persona.get("refusal_templates", [])
    if not templates:
        return "I can't help with that."
    return templates[0]


def redirect_message(persona: Dict) -> str:
    templates = persona.get("redirect_templates", [])
    if not templates:
        return "I'm open to playful attraction, but let's keep it suggestive rather than explicit."
    return templates[0]
