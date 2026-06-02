"""Runtime configuration for AMIII."""

from __future__ import annotations

from dataclasses import dataclass, replace
import os
from typing import Literal


ProviderMode = Literal["ollama", "groq", "auto"]


@dataclass(frozen=True)
class AMIIIConfig:
    """Configuration shared by AMIII runtime components."""

    provider: ProviderMode = "auto"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.1-8b-instant"
    groq_api_key: str | None = None
    enable_groq_fallback: bool = False
    request_timeout_seconds: float = 60.0
    piper_model_path: str | None = None
    sample_rate: int = 16000

    @classmethod
    def from_env(cls) -> "AMIIIConfig":
        """Build configuration from environment variables."""

        provider = _provider_from_env(os.getenv("AMIII_PROVIDER", "auto"))
        return cls(
            provider=provider,
            ollama_base_url=os.getenv("AMIII_OLLAMA_BASE_URL", cls.ollama_base_url),
            ollama_model=os.getenv("AMIII_OLLAMA_MODEL", cls.ollama_model),
            groq_base_url=os.getenv("AMIII_GROQ_BASE_URL", cls.groq_base_url),
            groq_model=os.getenv("AMIII_GROQ_MODEL", cls.groq_model),
            groq_api_key=os.getenv("GROQ_API_KEY"),
            enable_groq_fallback=_env_bool("AMIII_ENABLE_GROQ_FALLBACK", False),
            request_timeout_seconds=float(
                os.getenv("AMIII_REQUEST_TIMEOUT_SECONDS", cls.request_timeout_seconds)
            ),
            piper_model_path=os.getenv("AMIII_PIPER_MODEL_PATH"),
            sample_rate=int(os.getenv("AMIII_SAMPLE_RATE", cls.sample_rate)),
        )

    def with_overrides(
        self,
        *,
        provider: ProviderMode | None = None,
        enable_groq_fallback: bool | None = None,
    ) -> "AMIIIConfig":
        """Return a copy with CLI overrides applied."""

        updates: dict[str, object] = {}
        if provider is not None:
            updates["provider"] = provider
        if enable_groq_fallback is not None:
            updates["enable_groq_fallback"] = enable_groq_fallback
        return replace(self, **updates)


def _provider_from_env(value: str) -> ProviderMode:
    normalized = value.strip().lower()
    if normalized not in {"ollama", "groq", "auto"}:
        raise ValueError(
            "AMIII_PROVIDER must be one of: ollama, groq, auto."
        )
    return normalized  # type: ignore[return-value]


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
