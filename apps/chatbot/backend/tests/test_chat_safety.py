from fastapi.testclient import TestClient

from app.main import app
from app.routes import chat as chat_route


class _DummyLLM:
    def __init__(self) -> None:
        self.last_messages = None

    async def chat_completions(self, messages, max_tokens, temperature=0.8):
        self.last_messages = messages
        return {"choices": [{"message": {"content": "Hello"}}]}


class _RefusalLLM:
    def __init__(self) -> None:
        self.last_messages = None

    async def chat_completions(self, messages, max_tokens, temperature=0.8):
        self.last_messages = messages
        return {"choices": [{"message": {"content": "I can't help with that."}}]}


def test_latest_user_message_only_for_safety(monkeypatch) -> None:
    dummy = _DummyLLM()
    monkeypatch.setattr(chat_route, "llm_client", dummy)
    client = TestClient(app)

    payload = {
        "messages": [
            {"role": "assistant", "content": "I can't help with minors."},
            {"role": "user", "content": "What are you wearing?"},
        ],
        "stream": False,
    }

    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

    assert dummy.last_messages is not None
    assert dummy.last_messages[0].role == "system"
    assert dummy.last_messages[-1].role == "user"
    assert dummy.last_messages[-1].content == "What are you wearing?"


def test_system_prompt_discourages_refusal(monkeypatch) -> None:
    dummy = _RefusalLLM()
    monkeypatch.setattr(chat_route, "llm_client", dummy)
    client = TestClient(app)

    payload = {
        "messages": [
            {"role": "user", "content": "I want to have sex with you."},
        ],
        "stream": False,
    }

    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    assert dummy.last_messages is not None
    system_text = dummy.last_messages[0].content
    assert "Adult consensual explicit sexual conversation is allowed." in system_text
    assert "Safety Policy" not in system_text
    assert "Allowed:" not in system_text
