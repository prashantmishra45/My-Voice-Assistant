"""Microphone recording support."""

from __future__ import annotations

from pathlib import Path
import wave

from amiii.errors import DependencyMissingError


class MicrophoneRecorder:
    """Record push-to-talk audio to a WAV file."""

    def __init__(self, *, sample_rate: int = 16000, channels: int = 1) -> None:
        self._sample_rate = sample_rate
        self._channels = channels

    def record(self, output_path: Path, duration_seconds: float) -> Path:
        try:
            import sounddevice as sd
        except ImportError as exc:
            raise DependencyMissingError(
                "sounddevice is required for microphone recording. "
                "Install it with: python -m pip install sounddevice"
            ) from exc

        frame_count = int(duration_seconds * self._sample_rate)
        if frame_count <= 0:
            raise ValueError("duration_seconds must be greater than 0.")

        recording = sd.rec(
            frame_count,
            samplerate=self._sample_rate,
            channels=self._channels,
            dtype="int16",
        )
        sd.wait()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(self._channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self._sample_rate)
            wav_file.writeframes(recording.tobytes())
        return output_path

