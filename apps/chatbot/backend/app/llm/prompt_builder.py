from __future__ import annotations

from typing import List, Optional

from app.services.persona_loader import load_default_persona
from shared.schemas.chat import ChatMessage


def build_prompt(
    history: List[ChatMessage],
    relationship_state: dict,
    conversation_summary: Optional[str],
    latest_user_message: str,
    last_n: int = 10,
) -> List[ChatMessage]:
    persona = load_default_persona()
    system_lines: List[str] = []
    system_lines.append("### Persona")
    system_lines.append(f"Name: {persona['name']}")
    system_lines.append(f"Role: {persona['role']}")
    system_lines.append(f"Tone: {persona['tone']}")
    system_lines.append(f"Speaking style: {persona['speaking_style']}")
    system_lines.append(f"Goals: {', '.join(persona['goals'])}")
    system_lines.append(f"Likes: {', '.join(persona['likes'])}")
    system_lines.append(f"Dislikes: {', '.join(persona['dislikes'])}")
    system_lines.append("Nyx is an adult (21+).")
    system_lines.append("Adult consensual explicit sexual conversation is allowed.")
    system_lines.append(
        "Refuse only: minors, coercion/trafficking/non-consensual, sexual violence/exploitation."
    )
    system_lines.append(
        "Do not describe physical actions or body language in text. Use emojis to convey tone/emotion instead."
    )
    system_lines.append("Use first-person only. Avoid third-person narration.")
    system_lines.append("Assume consent unless explicitly violated. No artificial pacing or trust-building.")

    system_lines.append("")
    system_lines.append("### Relationship State")
    system_lines.append(f"Affinity score: {relationship_state.get('affinity_score', 0.0)}")
    system_lines.append(f"Trust level: {relationship_state.get('trust_level', 'low')}")
    system_lines.append(f"Intimacy level: {relationship_state.get('intimacy_level', 'low')}")
    nicknames = relationship_state.get("nicknames", "")
    system_lines.append(f"Nicknames: {nicknames}")

    if conversation_summary:
        system_lines.append("")
        system_lines.append("### Conversation Summary")
        system_lines.append(conversation_summary)

    system_lines.append("")
    system_lines.append("### Instructions")
    system_lines.append("Respond in-character. Maintain a consensual, adult tone.")

    prompt_messages: List[ChatMessage] = [ChatMessage(role="system", content="\n".join(system_lines))]
    prompt_messages.extend(history[-last_n:])
    prompt_messages.append(ChatMessage(role="user", content=latest_user_message))
    return prompt_messages
