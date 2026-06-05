"""Command-line entrypoint for AMIII."""

from __future__ import annotations
from amiii.tools.applications import ApplicationLauncher

import argparse
from pathlib import Path
import tempfile

# Load .env from the project root (two levels up from this file: src/amiii/ -> src/ -> root)
try:
    from dotenv import load_dotenv

    _env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=_env_path)
except ImportError:
    pass  # python-dotenv not installed; rely on real env vars

from amiii.audio import MicrophoneRecorder
from amiii.config import AMIIIConfig, ProviderMode
from amiii.conversation import ConversationEngine
from amiii.errors import AMIIIError
from amiii.llm import create_chat_provider
from amiii.stt import FasterWhisperTranscriber
from amiii.tts import PiperSpeaker


def _resolve_model_path(raw: str | None) -> str | None:
    """If the model path is relative, resolve it against the project root."""
    if not raw:
        return raw
    p = Path(raw)
    if p.is_absolute():
        return raw
    # Resolve relative to the project root (parent of src/)
    root = Path(__file__).resolve().parent.parent.parent
    return str(root / p)


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

def try_application_command(prompt: str) -> str | None:
    """Handle simple application-launch commands."""

    text = prompt.lower().strip()

    launcher = ApplicationLauncher()

    if text.startswith("open "):
        app_name = text.replace("open ", "", 1).strip()

        try:
            launcher.open_application(app_name)
            return f"Opening {app_name}."
        except ValueError:
            return None

    return None


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    provider_override: ProviderMode | None = args.provider
    config = AMIIIConfig.from_env().with_overrides(
        provider=provider_override,
        enable_groq_fallback=True if args.enable_groq_fallback else None,
    )

    # Resolve the piper model path to an absolute path
    resolved_model_path = _resolve_model_path(config.piper_model_path)

    try:
        chat_provider = create_chat_provider(config)

        if args.text:
            speaker = PiperSpeaker(resolved_model_path) if args.speak_text else None
            engine = ConversationEngine(chat_provider=chat_provider, speaker=speaker)
            response = engine.run_text_turn(args.text, speak=args.speak_text)
            print(response.content)
            return 0

        # Voice turn (default)
        transcriber = FasterWhisperTranscriber()
        voice_speaker = PiperSpeaker(resolved_model_path)
        recorder = MicrophoneRecorder(sample_rate=config.sample_rate)
        engine = ConversationEngine(
            chat_provider=chat_provider,
            transcriber=transcriber,
            speaker=voice_speaker,
        )

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            audio_path = Path(temp_file.name)
        print(f"Recording for {args.duration} seconds... (speak now)")
        recorder.record(audio_path, args.duration)

        print("Transcribing...")
        prompt = transcriber.transcribe(audio_path)

        if not prompt.strip():
            print("(Nothing was heard — check your microphone and try again.)")
            return 0

        print(f"You said: {prompt}")

        tool_response = try_application_command(prompt)

        if tool_response:
            voice_speaker.speak(tool_response)
            print(f"AMIII: {tool_response}")
            return 0

        response = engine.run_text_turn(prompt, speak=True)
        print(f"AMIII: {response.content}")
        return 0
    except (AMIIIError, ValueError, FileNotFoundError) as exc:
        parser.exit(status=2, message=f"AMIII setup/runtime error: {exc}\n")
