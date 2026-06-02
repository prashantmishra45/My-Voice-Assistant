# AMIII Project Context

## Mission

AMIII is a long-term, modular, voice-controlled AI operating assistant. It should grow from basic voice conversation into a personal AI operating companion that can reason, automate desktop and browser workflows, assist with code, remember useful context, and coordinate future tools or agents.

## Product Direction

AMIII is not just a chatbot. It should understand requests, plan actions, execute safe tasks, ask for confirmation before risky actions, and continuously evolve through independently testable modules.

## Engineering Principles

- Prefer local-first and free tooling.
- Keep the architecture modular and beginner-friendly.
- Explain and document meaningful changes.
- Use type hints and clear naming.
- Avoid monolithic files.
- Keep safety gates around messaging, deletion, shell execution, and other irreversible actions.
- Keep code and documentation synchronized by the end of each work session.

## Current Architecture

The current implementation is a v0.1 scaffold:

- Python package under `src/amiii`
- LLM provider abstraction with Ollama, Groq, and auto-fallback modes
- voice pipeline interfaces for microphone input, speech-to-text, text-to-speech, and conversation orchestration
- placeholder tool modules for future desktop, browser, file, coding, and memory capabilities
- documentation and test foundation

## Current Defaults

- Default provider mode: `auto`
- Default local provider: Ollama
- Optional fallback provider: Groq
- Default Ollama model: `llama3.1:8b`
- Default Groq model: `llama-3.1-8b-instant`
- First interaction mode: push-to-talk voice

## Next Engineering Step

Install and verify external voice dependencies, then run the manual v0.1 acceptance test:

1. record microphone audio
2. transcribe with faster-whisper
3. call Ollama or Groq
4. speak response with Piper
