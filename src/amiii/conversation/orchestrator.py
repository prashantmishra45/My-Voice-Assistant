"""Conversation orchestration for AMIII."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from amiii.llm.base import ChatMessage, ChatProvider, LLMResponse


class Transcriber(Protocol):
    def transcribe(self, audio_path: Path) -> str:
        """Convert audio to text."""


class Speaker(Protocol):
    def speak(self, text: str) -> None:
        """Speak text aloud."""


class ConversationEngine:
    """Coordinate transcription, model response, and speech output."""

    def __init__(
        self,
        *,
        chat_provider: ChatProvider,
        transcriber: Transcriber | None = None,
        speaker: Speaker | None = None,
        system_prompt: str | None = None,
    ) -> None:
        self._chat_provider = chat_provider
        self._transcriber = transcriber
        self._speaker = speaker
        self._system_prompt = system_prompt or (
            "You are AMIII, a modular AI operating assistant. "
            "Be helpful, concise, and ask before risky actions."
        )
        self._history: list[ChatMessage] = [
            ChatMessage(role="system", content=self._system_prompt)
        ]

    @property
    def history(self) -> tuple[ChatMessage, ...]:
        return tuple(self._history)

    def run_text_turn(self, prompt: str, *, speak: bool = False) -> LLMResponse:
        prompt = prompt.strip()
        if not prompt:
            raise ValueError("Prompt cannot be empty.")

        self._history.append(ChatMessage(role="user", content=prompt))
        response = self._chat_provider.chat(list(self._history))
        self._history.append(ChatMessage(role="assistant", content=response.content))

        if speak:
            if self._speaker is None:
                raise ValueError("A speaker is required when speak=True.")
            self._speaker.speak(response.content)
        return response

    def run_voice_turn(self, audio_path: Path) -> LLMResponse:
        if self._transcriber is None:
            raise ValueError("A transcriber is required for voice turns.")
        if self._speaker is None:
            raise ValueError("A speaker is required for voice turns.")

        prompt = self._transcriber.transcribe(audio_path)
        response = self.run_text_turn(prompt, speak=False)
        self._speaker.speak(response.content)
        return response

