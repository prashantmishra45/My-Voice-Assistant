# AMIII Vision Analysis

## Product Intent

AMIII should become a personal AI operating companion. The key product idea is not "chat with a model"; it is "ask an assistant to understand, plan, and act safely across the computer."

## Core Capability Groups

- Conversation: natural dialogue, explanation, questions, and user preference adaptation.
- Voice: wake word later, push-to-talk first, transcription, and spoken responses.
- Desktop control: opening apps, switching windows, and launching installed software.
- Browser automation: search, navigation, downloads, and form filling.
- Messaging and email: draft, review, and send only after confirmation.
- File management: create, move, rename, organize, and delete only after confirmation.
- Coding assistant: explain, modify, refactor, debug, and test code.
- GitHub integration: commits, pull request summaries, reviews, and contributor tracking.
- Research: compare sources, summarize findings, and generate reports.
- Memory: short-term context, long-term preferences, and task history.

## Main Product Risks

- Over-automation without user confirmation.
- Secret leakage through logs or commits.
- Fragile integrations with desktop apps and websites.
- A monolithic assistant that becomes hard to teach or maintain.
- Paid-service dependency creep.

## Architecture Implication

AMIII needs small capability modules, explicit provider interfaces, central safety checks, and a clear documentation trail. The v0.1 scaffold should already reflect the final modular shape even while only voice conversation is usable.

