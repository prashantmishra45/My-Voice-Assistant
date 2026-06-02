"""Ollama chat provider."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from amiii.config import AMIIIConfig
from amiii.errors import ProviderUnavailableError
from amiii.llm.base import ChatMessage, LLMResponse


class OllamaChatProvider:
    """Chat provider for a local Ollama server."""

    name = "ollama"

    def __init__(self, config: AMIIIConfig) -> None:
        self._base_url = config.ollama_base_url.rstrip("/")
        self._model = config.ollama_model
        self._timeout = config.request_timeout_seconds

    def chat(self, messages: list[ChatMessage]) -> LLMResponse:
        payload = {
            "model": self._model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            "stream": False,
        }
        request = Request(
            f"{self._base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self._timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ProviderUnavailableError(
                f"Ollama request failed with HTTP {exc.code}: {detail}"
            ) from exc
        except URLError as exc:
            raise ProviderUnavailableError(
                "Ollama is not reachable. Start Ollama and verify the model is pulled."
            ) from exc
        except TimeoutError as exc:
            raise ProviderUnavailableError("Ollama request timed out.") from exc

        message = body.get("message") or {}
        content = str(message.get("content") or "").strip()
        if not content:
            raise ProviderUnavailableError("Ollama returned an empty response.")
        return LLMResponse(content=content, provider_name=self.name, model=self._model)

