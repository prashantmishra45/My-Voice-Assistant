"""Shared LLM provider contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ChatMessage:
    """A single chat message."""

    role: str
    content: str


@dataclass(frozen=True)
class LLMResponse:
    """Normalized response from a model provider."""

    content: str
    provider_name: str
    model: str


class ChatProvider(Protocol):
    """Common interface for all AMIII chat providers."""

    name: str

    def chat(self, messages: list[ChatMessage]) -> LLMResponse:
        """Return a model response for the supplied messages."""

