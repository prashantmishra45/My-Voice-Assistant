import unittest
from unittest.mock import MagicMock, patch
from amiii.tools.browser import BrowserTool
from amiii.tools.intent_router import LLMIntentRouter, Intent
from amiii.llm.base import ChatMessage, LLMResponse


class BrowserToolTests(unittest.TestCase):
    def test_registry_contains_required_websites(self) -> None:
        tool = BrowserTool()
        required = {"youtube", "github", "linkedin", "amazon"}
        self.assertTrue(required.issubset(tool.WEBSITE_REGISTRY.keys()))

    def test_unsupported_website_raises_value_error(self) -> None:
        tool = BrowserTool()
        with self.assertRaises(ValueError):
            tool.open_website(None, "invalid_site")
        with self.assertRaises(ValueError):
            tool.search_website(None, "invalid_site", "query")
        with self.assertRaises(ValueError):
            tool.click_first_result(None, "invalid_site")
        with self.assertRaises(ValueError):
            tool.website_search("invalid_site", "query")


class FakeChatProvider:
    def __init__(self, response_content: str) -> None:
        self.response_content = response_content

    def chat(self, messages: list[ChatMessage]) -> LLMResponse:
        return LLMResponse(
            content=self.response_content,
            provider_name="fake",
            model="fake"
        )


class IntentRouterBrowserTests(unittest.TestCase):
    def test_website_search_intent_parsing(self) -> None:
        provider = FakeChatProvider(
            '{"action": "website_search", "website": "GitHub", "query": "machine learning projects"}'
        )
        router = LLMIntentRouter(provider)
        intent = router.parse("Search GitHub for machine learning projects")
        self.assertEqual(intent.action, "website_search")
        self.assertEqual(intent.website, "GitHub")
        self.assertEqual(intent.query, "machine learning projects")

    def test_whatsapp_message_intent_parsing(self) -> None:
        provider = FakeChatProvider(
            '{"action": "whatsapp_message", "contact": "Mom", "message": "I will be late"}'
        )
        router = LLMIntentRouter(provider)
        intent = router.parse("Open WhatsApp and message Mom: I will be late")
        self.assertEqual(intent.action, "whatsapp_message")
        self.assertEqual(intent.contact, "Mom")
        self.assertEqual(intent.message, "I will be late")


class BrowserToolIntegrationTests(unittest.TestCase):
    @patch("amiii.safety.confirmation.ConfirmationService.confirm")
    def test_whatsapp_message_cancelled(self, mock_confirm: MagicMock) -> None:
        mock_confirm.return_value = False
        tool = BrowserTool()
        result = tool.send_whatsapp_message("John", "Hello")
        self.assertEqual(result, "Message sending cancelled by user.")

