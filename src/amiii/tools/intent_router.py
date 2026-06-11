from __future__ import annotations

import json
import re
from dataclasses import dataclass

from amiii.llm.base import ChatMessage, ChatProvider


@dataclass
class Intent:
    action: str
    target: str | None = None
    website: str | None = None
    query: str | None = None
    contact: str | None = None
    message: str | None = None


class LLMIntentRouter:

    VALID_ACTIONS = {
        "open_application",
        "google_search",
        "open_website",
        "play_media",
        "chat",
        "website_search",
        "whatsapp_message",
    }

    def __init__(self, chat_provider: ChatProvider):
        self._chat_provider = chat_provider

    def parse(self, user_text: str) -> Intent:

        router_prompt = f"""
You are an intent classification engine.

Your job is to classify the user's request.

Allowed actions:

1. open_application
2. google_search
3. open_website
4. play_media
5. chat
6. website_search
7. whatsapp_message

Rules:

- Return EXACTLY one JSON object.
- Return ONLY JSON.
- Do NOT explain anything.
- Do NOT use markdown.
- Do NOT use code blocks.
- Do NOT invent actions.
- Do NOT invent fields.

Examples:

User: Open Chrome
{{"action":"open_application","target":"chrome"}}

User: Please launch VS Code
{{"action":"open_application","target":"vs code"}}

User: Open YouTube
{{"action":"open_website","target":"youtube"}}

User: Open GitHub
{{"action":"open_website","target":"github"}}

User: Search Google for Python tutorials
{{"action":"google_search","target":"python tutorials"}}

User: Find Java roadmap on Google
{{"action":"google_search","target":"java roadmap"}}

User: Play Believer song
{{"action":"play_media","target":"Believer song"}}

User: Play relaxing music on YouTube
{{"action":"play_media","target":"relaxing music"}}

User: Search YouTube for Python tutorials
{{"action":"website_search","website":"youtube","query":"Python tutorials"}}

User: Search GitHub for machine learning projects
{{"action":"website_search","website":"github","query":"machine learning projects"}}

User: Search LinkedIn for internships
{{"action":"website_search","website":"linkedin","query":"internships"}}

User: Search Amazon for Logitech mouse
{{"action":"website_search","website":"amazon","query":"Logitech mouse"}}

User: Message Prashant on WhatsApp saying Hello
{{"action":"whatsapp_message","contact":"Prashant","message":"Hello"}}

User: Send a WhatsApp message to John: Are you coming today?
{{"action":"whatsapp_message","contact":"John","message":"Are you coming today?"}}

User: Open WhatsApp and message Mom: I will be late
{{"action":"whatsapp_message","contact":"Mom","message":"I will be late"}}

User: What is the capital of India?
{{"action":"chat"}}

User: My name is Prashant.
{{"action":"chat"}}

User: Tell me a joke.
{{"action":"chat"}}

Now classify this request:

{user_text}
"""

        response = self._chat_provider.chat(
            [
                ChatMessage(
                    role="user",
                    content=router_prompt
                )
            ]
        )

        print("\nRAW ROUTER RESPONSE:")
        print(response.content)
        print()

        try:

            json_match = re.search(
                r"\{[^{}]*\}",
                response.content,
                re.DOTALL
            )

            if not json_match:
                return Intent(action="chat")

            data = json.loads(json_match.group())

            action = data.get("action", "chat")

            if action not in self.VALID_ACTIONS:
                return Intent(action="chat")

            return Intent(
                action=action,
                target=data.get("target"),
                website=data.get("website"),
                query=data.get("query"),
                contact=data.get("contact"),
                message=data.get("message")
            )

        except Exception as e:

            print(f"Router error: {e}")

            return Intent(action="chat")