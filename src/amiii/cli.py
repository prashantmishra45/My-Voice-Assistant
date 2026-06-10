"""Command-line entrypoint for AMIII."""

from __future__ import annotations
from amiii.tools.applications import ApplicationLauncher
from amiii.tools.intent_router import LLMIntentRouter
from amiii.tools.registry import ToolRegistry, RegisteredTool
from amiii.llm.base import ChatProvider

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

def get_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    launcher = ApplicationLauncher()
    
    registry.register(RegisteredTool(
        name="open_application",
        description="Open a Windows application or folder",
        handler=launcher.open_application
    ))
    registry.register(RegisteredTool(
        name="google_search",
        description="Search Google using the default browser",
        handler=launcher.google_search
    ))
    registry.register(RegisteredTool(
        name="open_website",
        description="Open a specific website",
        handler=launcher.open_website
    ))
    registry.register(RegisteredTool(
        name="play_media",
        description="Search YouTube and open results for playback",
        handler=launcher.play_media
    ))
    return registry

def try_tool_command(
    prompt: str,
    chat_provider: ChatProvider,
) -> str | None:

    router = LLMIntentRouter(chat_provider)
    intent = router.parse(prompt)

    print(f"Detected intent: {intent}")
    
    if intent.action == "chat":
        return None

    registry = get_tool_registry()

    try:
        tool = registry.get(intent.action)
        if intent.target:
            return tool.handler(intent.target)
        else:
            return tool.handler()
    except KeyError:
        print(f"Tool {intent.action} not found in registry.")
        return None
    except ValueError as e:
        print(f"Tool value error: {e}")
        return None
    except Exception as e:
        print(f"Tool execution error: {e}")
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
            
            tool_response = try_tool_command(args.text, chat_provider)
            if tool_response:
                if speaker:
                    speaker.speak(tool_response)
                print(f"AMIII: {tool_response}")
                return 0
                
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
        print("AMIII is listening. Say 'goodbye' to exit.")

        while True:

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as temp_file:
                audio_path = Path(temp_file.name)

            print(f"\nRecording for {args.duration} seconds...")
            recorder.record(audio_path, args.duration)

            print("Transcribing...")
            prompt = transcriber.transcribe(audio_path)

            if not prompt.strip():
                print("(Nothing was heard.)")
                continue

            print(f"You said: {prompt}")

            if "goodbye" in prompt.lower():
                voice_speaker.speak("Goodbye. Have a nice day.")
                print("AMIII: Goodbye.")
                break

            tool_response = try_tool_command(
                prompt,
                chat_provider
            )

            if tool_response:
                voice_speaker.speak(tool_response)
                print(f"AMIII: {tool_response}")
                continue

            response = engine.run_text_turn(prompt, speak=True)

            print(f"AMIII: {response.content}")

        return 0
    except (AMIIIError, ValueError, FileNotFoundError) as exc:
        parser.exit(status=2, message=f"AMIII setup/runtime error: {exc}\n")
