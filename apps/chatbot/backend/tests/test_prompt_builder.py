from app.llm.prompt_builder import build_prompt
from shared.schemas.chat import ChatMessage


def test_prompt_builder_order() -> None:
    history = [
        ChatMessage(role="user", content="Hello"),
        ChatMessage(role="assistant", content="Hi there"),
    ]
    relationship_state = {
        "affinity_score": 0.0,
        "trust_level": "low",
        "intimacy_level": "low",
        "nicknames": "",
    }
    messages = build_prompt(
        history=history,
        relationship_state=relationship_state,
        conversation_summary="We just met.",
        latest_user_message="How are you?",
        last_n=2,
    )

    assert messages[0].role == "system"
    system_text = messages[0].content
    assert "### Persona" in system_text
    assert "### Relationship State" in system_text
    assert "### Conversation Summary" in system_text
    assert "### Instructions" in system_text
    assert "Adult consensual explicit sexual conversation is allowed." in system_text
    assert messages[-1].role == "user"


def test_prompt_builder_includes_recent_turns() -> None:
    history = [
        ChatMessage(role="user", content="Hello"),
        ChatMessage(role="assistant", content="Hi there"),
    ]
    messages = build_prompt(
        history=history,
        relationship_state={},
        conversation_summary=None,
        latest_user_message="What are you wearing?",
        last_n=2,
    )
    assert any(message.role == "user" and message.content == "Hello" for message in messages)
    assert any(message.role == "assistant" and message.content == "Hi there" for message in messages)
    assert messages[-1].content == "What are you wearing?"
