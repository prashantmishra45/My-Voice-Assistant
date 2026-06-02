# Engineering Journal: 2026-06-02

## Tasks Completed

- Read the AMIII Engineering Constitution and Product Vision.
- Created the initial repository structure.
- Added project context, roadmap, architecture, setup, feature, decision, contribution, and changelog documentation.
- Scaffolded the Python package for voice conversation and LLM provider routing.
- Added initial tests.

## Challenges

- The workspace started empty except for Git metadata.
- Ollama, Piper, FFmpeg, and pytest were not installed on PATH.

## Solutions

- Used a dependency-light scaffold so imports and tests can run before voice dependencies are installed.
- Used Python's built-in `unittest` for initial verification.
- Documented missing external dependencies in `setup/external_requirements.md`.

## Learnings

- AMIII should support both strict documentation-first work and pragmatic fast-build exceptions.
- Provider abstraction is valuable immediately because the project will support Ollama and Groq.

## Next Steps

- Install Ollama and pull a local model.
- Default Ollama model selected for the project: `llama3.1:8b`.
- Install faster-whisper and sounddevice.
- Install Piper and configure a voice model.
- Run the manual v0.1 voice acceptance test.
