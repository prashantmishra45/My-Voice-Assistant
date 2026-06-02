from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from amiii.conversation import ConversationEngine
from amiii.llm.base import ChatMessage, LLMResponse


class FakeChatProvider:
    name = "fake"

    def __init__(self) -> None:
        self.messages: list[ChatMessage] = []

    def chat(self, messages: list[ChatMessage]) -> LLMResponse:
        self.messages = messages
        return LLMResponse(content="hello human", provider_name="fake", model="fake")


class FakeTranscriber:
    def transcribe(self, audio_path: Path) -> str:
        return "what can you do"


class FakeSpeaker:
    def __init__(self) -> None:
        self.spoken: list[str] = []

    def speak(self, text: str) -> None:
        self.spoken.append(text)


class ConversationEngineTests(unittest.TestCase):
    def test_text_turn_updates_history(self) -> None:
        provider = FakeChatProvider()
        engine = ConversationEngine(chat_provider=provider)

        response = engine.run_text_turn("hello")

        self.assertEqual(response.content, "hello human")
        self.assertEqual(engine.history[-2].role, "user")
        self.assertEqual(engine.history[-1].role, "assistant")
        self.assertIn("AMIII", provider.messages[0].content)

    def test_empty_prompt_is_rejected(self) -> None:
        engine = ConversationEngine(chat_provider=FakeChatProvider())
        with self.assertRaises(ValueError):
            engine.run_text_turn("   ")

    def test_voice_turn_transcribes_and_speaks(self) -> None:
        provider = FakeChatProvider()
        speaker = FakeSpeaker()
        engine = ConversationEngine(
            chat_provider=provider,
            transcriber=FakeTranscriber(),
            speaker=speaker,
        )

        with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
            response = engine.run_voice_turn(Path(temp_file.name))

        self.assertEqual(response.content, "hello human")
        self.assertEqual(speaker.spoken, ["hello human"])
        self.assertEqual(engine.history[-2].content, "what can you do")


if __name__ == "__main__":
    unittest.main()

