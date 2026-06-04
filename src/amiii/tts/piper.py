"""Piper text-to-speech support using the piper-tts Python API."""

from __future__ import annotations

import io
from pathlib import Path
import sys
import tempfile
import wave

from amiii.errors import ConfigurationError, DependencyMissingError


class PiperSpeaker:
    """Speak text using the piper-tts Python package."""

    def __init__(self, model_path: str | None) -> None:
        if not model_path:
            raise ConfigurationError(
                "AMIII_PIPER_MODEL_PATH is required for Piper text-to-speech. "
                "Set it in your .env file, e.g.: AMIII_PIPER_MODEL_PATH=models/piper/en_US-amy-medium.onnx"
            )
        self._model_path = Path(model_path)
        self._voice = None  # lazy-loaded

    def _load_voice(self):
        if self._voice is not None:
            return self._voice
        try:
            from piper import PiperVoice
        except ImportError as exc:
            raise DependencyMissingError(
                "piper-tts is required for text-to-speech. "
                "Install it with: python -m pip install piper-tts"
            ) from exc
        if not self._model_path.exists():
            raise ConfigurationError(
                f"Piper model file not found: {self._model_path}\n"
                "Download it and place it at the path set in AMIII_PIPER_MODEL_PATH."
            )
        self._voice = PiperVoice.load(str(self._model_path))
        return self._voice

    def speak(self, text: str) -> None:
        if not text.strip():
            return

        voice = self._load_voice()

        # synthesize_wav() sets WAV headers (channels, sample rate, width) automatically.
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)

        wav_bytes = wav_buffer.getvalue()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wav_bytes)
            output_path = Path(tmp.name)

        self._play_wav(output_path)

    def _play_wav(self, output_path: Path) -> None:
        if sys.platform.startswith("win"):
            import winsound
            winsound.PlaySound(str(output_path), winsound.SND_FILENAME)
            return
        # Linux / macOS fallback
        try:
            import sounddevice as sd
            import soundfile as sf
            data, samplerate = sf.read(str(output_path))
            sd.play(data, samplerate)
            sd.wait()
        except ImportError:
            raise DependencyMissingError(
                "On non-Windows systems, sounddevice and soundfile are required for playback."
            )
