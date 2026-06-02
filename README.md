# AMIII

AMIII is a modular, voice-controlled AI operating assistant. The long-term goal is a personal AI operating companion that can converse, reason, automate desktop and browser tasks, assist with coding, remember useful context, and coordinate future tool or agent modules.

This repository is intentionally documentation-heavy because AMIII is also a learning project. Every meaningful feature should leave behind architecture notes, setup guidance, tests, and a journal entry.

## Current Status

Version: `0.1.0`

Implemented foundation:

- required project structure
- documentation skeleton
- Python package scaffold
- configurable LLM provider layer
- Ollama adapter
- Groq adapter
- `auto` provider mode with optional Groq fallback
- voice pipeline interfaces for microphone input, faster-whisper STT, Piper TTS, and conversation orchestration
- unit tests for structure, provider selection, and orchestration

## Quick Start

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[voice,dev]"
```

Copy `.env.example` to `.env` and fill in values as needed. AMIII never stores real API keys in the repository.

Run a text prompt through the configured provider:

```powershell
$env:PYTHONPATH="src"
python -m amiii --text "Hello AMIII" --provider auto
```

Run the push-to-talk voice loop after installing voice dependencies and configuring Piper:

```powershell
$env:PYTHONPATH="src"
python -m amiii --voice --duration 5
```

## Provider Modes

- `ollama`: local-only. Requires Ollama running locally and a pulled model.
- `groq`: cloud-only. Requires `GROQ_API_KEY`.
- `auto`: tries Ollama first, then Groq when fallback is enabled and configured.

## Documentation Map

- `PROJECT_CONTEXT.md`: high-level project memory
- `architecture/scalable_architecture.md`: system architecture
- `docs/roadmap.md`: v0.1 to v1.0 roadmap
- `setup/external_requirements.md`: required external software
- `docs/features/`: feature specs
- `docs/decisions/`: architecture decision records
- `docs/journal/`: engineering journal
- `docs/contributions/`: contribution tracking

## Tests

The initial tests use Python's built-in `unittest` so they can run before dev dependencies are installed:

```powershell
python -m unittest discover -s tests
```
