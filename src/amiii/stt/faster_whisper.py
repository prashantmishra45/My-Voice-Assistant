"""faster-whisper transcription support."""

from __future__ import annotations

from pathlib import Path

from amiii.errors import DependencyMissingError


class FasterWhisperTranscriber:
    """Transcribe local audio files with faster-whisper."""

    def __init__(self, model_size: str = "base", device: str = "cpu") -> None:
        self._model_size = model_size
        self._device = device
        self._model = None

    def transcribe(self, audio_path: Path) -> str:
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file does not exist: {audio_path}")
        model = self._load_model()
        segments, _info = model.transcribe(str(audio_path))
        text = " ".join(segment.text.strip() for segment in segments).strip()
        return text

    def _load_model(self):
        if self._model is not None:
            return self._model
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise DependencyMissingError(
                "faster-whisper is required for speech-to-text. "
                "Install it with: python -m pip install faster-whisper"
            ) from exc
        self._model = WhisperModel(self._model_size, device=self._device)
        return self._model

