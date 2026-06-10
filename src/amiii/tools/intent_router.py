from __future__ import annotations

import json
import re
from dataclasses import dataclass

from amiii.llm.base import ChatMessage, ChatProvider


@dataclass
class Intent:
    action: str
    target: str | None = None


class LLMIntentRouter:

    VALID_ACTIONS = {
        "open_application",
        "google_search",
        "open_website",
        "play_media",
        "chat",
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
                target=data.get("target")
            )

        except Exception as e:

            print(f"Router error: {e}")

            return Intent(action="chat")