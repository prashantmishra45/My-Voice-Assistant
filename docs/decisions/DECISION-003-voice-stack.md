# DECISION-003: Initial Voice Stack

## Problem

AMIII needs a local-first voice pipeline for v0.1.

## Options Considered

- Browser-based speech APIs.
- Paid hosted speech APIs.
- Local faster-whisper STT and Piper TTS.

## Chosen Option

Use faster-whisper for speech-to-text and Piper for text-to-speech, with push-to-talk recording first.

## Reasoning

This matches the local-first preference and avoids paid services. Push-to-talk is simpler and safer than always-listening wake word behavior for the first version.

## Tradeoffs

- Setup is heavier than a hosted API.
- Local performance depends on the user's machine.

## Future Impact

Wake word, continuous listening, and alternate TTS voices can be added without replacing the conversation engine.

