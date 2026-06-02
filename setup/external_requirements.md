# External Requirements

AMIII must never assume external tools already exist. This file tracks required software, why it is needed, how to install it, and how to verify it.

## Current Environment Snapshot

Date checked: 2026-06-02

| Requirement | Purpose | Status |
| --- | --- | --- |
| Python | Runtime and development language | Installed: Python 3.13.7 |
| Git | Version control and collaboration | Installed: Git 2.52.0.windows.1 |
| VS Code | Recommended editor | Installed: 1.122.1 |
| Ollama | Local LLM runtime | Not found on PATH |
| Piper | Local text-to-speech | Not found on PATH |
| FFmpeg | Audio conversion utility for future workflows | Not found on PATH |
| Groq API key | Optional free cloud fallback LLM | User-provided, not stored in repo |

## Python

Purpose: runs AMIII and its development tools.

Install:

1. Download Python from `https://www.python.org/downloads/`.
2. Enable "Add Python to PATH" during installation.

Verify:

```powershell
python --version
```

## Git

Purpose: source control, pull requests, and contribution tracking.

Install:

1. Download Git for Windows from `https://git-scm.com/download/win`.
2. Accept the default installation options unless your team has different standards.

Verify:

```powershell
git --version
```

## Ollama

Purpose: local-first LLM provider.

Install:

1. Download Ollama from `https://ollama.com/download`.
2. Install it for Windows.
3. Pull a model, for example:

```powershell
ollama pull llama3.1:8b
```

Verify:

```powershell
ollama --version
ollama list
```

## Groq API Key

Purpose: optional cloud fallback or user-selected LLM provider.

Setup:

1. Create a Groq API key in your Groq account.
2. Store it as an environment variable:

```powershell
$env:GROQ_API_KEY="your_key_here"
```

Verify:

```powershell
python -c "import os; print(bool(os.getenv('GROQ_API_KEY')))"
```

Do not commit `.env` or real API keys.

## faster-whisper

Purpose: speech-to-text for voice input.

Install:

```powershell
python -m pip install faster-whisper
```

Verify:

```powershell
python -c "import faster_whisper; print('faster-whisper ready')"
```

## sounddevice

Purpose: microphone recording.

Install:

```powershell
python -m pip install sounddevice
```

Verify:

```powershell
python -c "import sounddevice; print('sounddevice ready')"
```

## Piper

Purpose: local text-to-speech.

Install:

```powershell
python -m pip install piper-tts
```

Alternative install:

1. Install Piper from its official releases or package instructions.
2. Download a compatible voice model.
3. Set `AMIII_PIPER_MODEL_PATH` to the model path.

Verify:

```powershell
piper --help
```
