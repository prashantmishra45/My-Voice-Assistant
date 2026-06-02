"""Provider selection for AMIII."""

from __future__ import annotations

from collections.abc import Callable

from amiii.config import AMIIIConfig
from amiii.errors import ConfigurationError, ProviderUnavailableError
from amiii.llm.base import ChatMessage, ChatProvider, LLMResponse
from amiii.llm.groq import GroqChatProvider
from amiii.llm.ollama import OllamaChatProvider

ProviderBuilder = Callable[[AMIIIConfig], ChatProvider]


class AutoFallbackChatProvider:
    """Try a primary provider, then a configured fallback provider."""

    name = "auto"

    def __init__(
        self,
        primary: ChatProvider,
        fallback: ChatProvider | None,
    ) -> None:
        self._primary = primary
        self._fallback = fallback

    def chat(self, messages: list[ChatMessage]) -> LLMResponse:
        try:
            return self._primary.chat(messages)
        except ProviderUnavailableError:
            if self._fallback is None:
                raise
            return self._fallback.chat(messages)


def create_chat_provider(
    config: AMIIIConfig,
    *,
    ollama_builder: ProviderBuilder = OllamaChatProvider,
    groq_builder: ProviderBuilder = GroqChatProvider,
) -> ChatProvider:
    """Create the selected chat provider from configuration."""

    if config.provider == "ollama":
        return ollama_builder(config)
    if config.provider == "groq":
        return groq_builder(config)
    if config.provider == "auto":
        primary = ollama_builder(config)
        fallback = None
        if config.enable_groq_fallback:
            if not config.groq_api_key:
                raise ConfigurationError(
                    "Auto mode has Groq fallback enabled, but GROQ_API_KEY is missing."
                )
            fallback = groq_builder(config)
        return AutoFallbackChatProvider(primary, fallback)
    raise ConfigurationError(f"Unsupported provider mode: {config.provider}")

