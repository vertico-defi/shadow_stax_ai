from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator, Dict, List, Tuple

import httpx

from shared.config.settings import get_settings
from shared.schemas.chat import ChatMessage
from shared.logging.logger import get_logger

settings = get_settings()
logger = get_logger("llm-client")


class LLMClient:
    def __init__(self) -> None:
        self._semaphore = asyncio.Semaphore(settings.llm_concurrency_limit)
        self._timeout = httpx.Timeout(settings.llm_request_timeout_seconds)
        self._base_url = settings.llm_base_url.rstrip("/")
        self._model = settings.llm_model
        self._api_mode = settings.llm_api_mode.lower()

    def _endpoint(self, path: str) -> str:
        return f"{self._base_url}/{path.lstrip('/')}"

    async def chat_completions(
        self,
        messages: List[ChatMessage],
        max_tokens: int,
        temperature: float = 0.8,
    ) -> Dict[str, Any]:
        if self._api_mode == "ollama":
            payload = {
                "model": self._model,
                "messages": [message.model_dump() for message in messages],
                "stream": False,
                "options": {"temperature": temperature},
            }
            endpoint = self._endpoint("/api/chat")
        else:
            payload = {
                "model": self._model,
                "messages": [message.model_dump() for message in messages],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False,
            }
            endpoint = self._endpoint("/chat/completions")
        async with self._semaphore:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
                if self._api_mode == "ollama":
                    content = data.get("message", {}).get("content", "")
                    return {"choices": [{"message": {"content": content}}]}
                return data

    async def stream_chat_completions(
        self,
        messages: List[ChatMessage],
        max_tokens: int,
        temperature: float = 0.8,
    ) -> AsyncGenerator[Tuple[str, str], None]:
        if self._api_mode == "ollama":
            payload = {
                "model": self._model,
                "messages": [message.model_dump() for message in messages],
                "stream": True,
                "options": {"temperature": temperature},
            }
            endpoint = self._endpoint("/api/chat")
        else:
            payload = {
                "model": self._model,
                "messages": [message.model_dump() for message in messages],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True,
            }
            endpoint = self._endpoint("/chat/completions")
        async with self._semaphore:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                async with client.stream("POST", endpoint, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        if self._api_mode == "ollama":
                            try:
                                payload = json.loads(line)
                            except json.JSONDecodeError:
                                logger.warning("llm_stream_parse_failed payload=%s", line)
                                continue
                            if payload.get("done"):
                                yield ("done", "")
                                return
                            content = payload.get("message", {}).get("content", "")
                            yield ("delta", content)
                        else:
                            if not line.startswith("data:"):
                                continue
                            data = line.replace("data:", "", 1).strip()
                            if data == "[DONE]":
                                yield ("done", "")
                                return
                            try:
                                payload = json.loads(data)
                            except json.JSONDecodeError:
                                logger.warning("llm_stream_parse_failed payload=%s", data)
                                continue
                            delta = payload.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            yield ("delta", content)
