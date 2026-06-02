"""Command-line entrypoint for AMIII."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile

from amiii.audio import MicrophoneRecorder
from amiii.config import AMIIIConfig, ProviderMode
from amiii.conversation import ConversationEngine
from amiii.errors import AMIIIError
from amiii.llm import create_chat_provider
from amiii.stt import FasterWhisperTranscriber
from amiii.tts import PiperSpeaker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AMIII.")
    parser.add_argument("--text", help="Run a text-only turn instead of voice input.")
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Run a push-to-talk voice turn. This is the default when --text is absent.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=5.0,
        help="Voice recording duration in seconds.",
    )
    parser.add_argument(
        "--provider",
        choices=["ollama", "groq", "auto"],
        help="Override the configured provider mode.",
    )
    parser.add_argument(
        "--enable-groq-fallback",
        action="store_true",
        help="Enable Groq fallback when provider mode is auto.",
    )
    parser.add_argument(
        "--speak-text",
        action="store_true",
        help="Speak responses during --text runs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    provider_override: ProviderMode | None = args.provider
    config = AMIIIConfig.from_env().with_overrides(
        provider=provider_override,
        enable_groq_fallback=True if args.enable_groq_fallback else None,
    )

    try:
        chat_provider = create_chat_provider(config)
        speaker = PiperSpeaker(config.piper_model_path) if args.speak_text else None
        engine = ConversationEngine(chat_provider=chat_provider, speaker=speaker)

        if args.text:
            response = engine.run_text_turn(args.text, speak=args.speak_text)
            print(response.content)
            return 0

        voice_speaker = PiperSpeaker(config.piper_model_path)
        transcriber = FasterWhisperTranscriber()
        recorder = MicrophoneRecorder(sample_rate=config.sample_rate)
        engine = ConversationEngine(
            chat_provider=chat_provider,
            transcriber=transcriber,
            speaker=voice_speaker,
        )

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            audio_path = Path(temp_file.name)
        print(f"Recording for {args.duration} seconds...")
        recorder.record(audio_path, args.duration)
        response = engine.run_voice_turn(audio_path)
        print(response.content)
        return 0
    except (AMIIIError, ValueError, FileNotFoundError) as exc:
        parser.exit(status=2, message=f"AMIII setup/runtime error: {exc}\n")

