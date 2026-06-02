"""Piper text-to-speech support."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from amiii.errors import ConfigurationError, DependencyMissingError


class PiperSpeaker:
    """Speak text using the Piper command-line tool."""

    def __init__(self, model_path: str | None) -> None:
        if not model_path:
            raise ConfigurationError(
                "AMIII_PIPER_MODEL_PATH is required for Piper text-to-speech."
            )
        self._model_path = Path(model_path)

    def speak(self, text: str) -> None:
        if not text.strip():
            return
        piper_path = shutil.which("piper")
        if piper_path is None:
            raise DependencyMissingError(
                "Piper is required for text-to-speech, but 'piper' was not found on PATH."
            )
        if not self._model_path.exists():
            raise ConfigurationError(f"Piper model file not found: {self._model_path}")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            output_path = Path(temp_file.name)

        command = [
            piper_path,
            "--model",
            str(self._model_path),
            "--output_file",
            str(output_path),
        ]
        subprocess.run(
            command,
            input=text,
            text=True,
            check=True,
            capture_output=True,
        )
        self._play_wav(output_path)

    def _play_wav(self, output_path: Path) -> None:
        if sys.platform.startswith("win"):
            import winsound

            winsound.PlaySound(str(output_path), winsound.SND_FILENAME)
            return
        raise DependencyMissingError(
            "Automatic WAV playback is only implemented for Windows in v0.1."
        )

