# DECISION-002: Ollama Local-First With Groq Fallback

## Problem

AMIII needs an LLM provider strategy that respects local-first goals while still allowing progress when local models are unavailable or too slow.

## Options Considered

- Require Ollama only.
- Use Groq as the primary provider.
- Use Ollama by default and Groq as user-selected provider or fallback.

## Chosen Option

Use Ollama as the default local provider. Support Groq as both a user-selectable provider and an optional fallback in `auto` mode.

## Reasoning

Ollama keeps AMIII private and local-first. Groq gives a free cloud path when the user chooses it or when local setup is not ready.

## Tradeoffs

- Groq requires internet access and an API key.
- Provider abstraction adds some upfront structure.

## Future Impact

New providers can be added behind the same `ChatProvider` interface.

