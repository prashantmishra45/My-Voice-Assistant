"""Groq chat provider using the OpenAI-compatible API."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from amiii.config import AMIIIConfig
from amiii.errors import ConfigurationError, ProviderUnavailableError
from amiii.llm.base import ChatMessage, LLMResponse


class GroqChatProvider:
    """Chat provider for Groq's OpenAI-compatible endpoint."""

    name = "groq"

    def __init__(self, config: AMIIIConfig) -> None:
        if not config.groq_api_key:
            raise ConfigurationError(
                "GROQ_API_KEY is required when using the Groq provider."
            )
        self._base_url = config.groq_base_url.rstrip("/")
        self._model = config.groq_model
        self._api_key = config.groq_api_key
        self._timeout = config.request_timeout_seconds

    def chat(self, messages: list[ChatMessage]) -> LLMResponse:
        payload = {
            "model": self._model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
        }
        request = Request(
            f"{self._base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self._timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ProviderUnavailableError(
                f"Groq request failed with HTTP {exc.code}: {detail}"
            ) from exc
        except URLError as exc:
            raise ProviderUnavailableError(
                "Groq is not reachable. Check internet access and GROQ_API_KEY."
            ) from exc
        except TimeoutError as exc:
            raise ProviderUnavailableError("Groq request timed out.") from exc

        choices = body.get("choices") or []
        if not choices:
            raise ProviderUnavailableError("Groq returned no choices.")
        message = choices[0].get("message") or {}
        content = str(message.get("content") or "").strip()
        if not content:
            raise ProviderUnavailableError("Groq returned an empty response.")
        return LLMResponse(content=content, provider_name=self.name, model=self._model)

