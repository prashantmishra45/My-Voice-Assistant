from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from amiii.config import AMIIIConfig
from amiii.errors import ConfigurationError, ProviderUnavailableError
from amiii.llm.base import ChatMessage, LLMResponse
from amiii.llm.factory import create_chat_provider


class FakeProvider:
    def __init__(self, name: str, *, fail: bool = False) -> None:
        self.name = name
        self.fail = fail

    def chat(self, messages: list[ChatMessage]) -> LLMResponse:
        if self.fail:
            raise ProviderUnavailableError(f"{self.name} failed")
        return LLMResponse(
            content=f"{self.name} response",
            provider_name=self.name,
            model=f"{self.name}-model",
        )


def build_ollama(config: AMIIIConfig):
    return FakeProvider("ollama")


def build_failed_ollama(config: AMIIIConfig):
    return FakeProvider("ollama", fail=True)


def build_groq(config: AMIIIConfig):
    return FakeProvider("groq")


class LLMFactoryTests(unittest.TestCase):
    def test_ollama_mode_returns_ollama_provider(self) -> None:
        config = AMIIIConfig(provider="ollama")
        provider = create_chat_provider(config, ollama_builder=build_ollama)
        response = provider.chat([ChatMessage(role="user", content="hello")])
        self.assertEqual(response.provider_name, "ollama")

    def test_groq_mode_requires_api_key_in_real_builder_path(self) -> None:
        config = AMIIIConfig(provider="groq", groq_api_key=None)
        with self.assertRaises(ConfigurationError):
            create_chat_provider(config)

    def test_groq_mode_returns_groq_provider_when_builder_supplied(self) -> None:
        config = AMIIIConfig(provider="groq", groq_api_key="test-key")
        provider = create_chat_provider(config, groq_builder=build_groq)
        response = provider.chat([ChatMessage(role="user", content="hello")])
        self.assertEqual(response.provider_name, "groq")

    def test_auto_uses_ollama_first(self) -> None:
        config = AMIIIConfig(provider="auto")
        provider = create_chat_provider(config, ollama_builder=build_ollama)
        response = provider.chat([ChatMessage(role="user", content="hello")])
        self.assertEqual(response.provider_name, "ollama")

    def test_auto_falls_back_to_groq_when_enabled(self) -> None:
        config = AMIIIConfig(
            provider="auto",
            enable_groq_fallback=True,
            groq_api_key="test-key",
        )
        provider = create_chat_provider(
            config,
            ollama_builder=build_failed_ollama,
            groq_builder=build_groq,
        )
        response = provider.chat([ChatMessage(role="user", content="hello")])
        self.assertEqual(response.provider_name, "groq")

    def test_auto_fallback_requires_groq_key(self) -> None:
        config = AMIIIConfig(provider="auto", enable_groq_fallback=True)
        with self.assertRaises(ConfigurationError):
            create_chat_provider(config, ollama_builder=build_ollama)


if __name__ == "__main__":
    unittest.main()

