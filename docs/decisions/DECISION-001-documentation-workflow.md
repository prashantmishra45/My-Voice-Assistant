# DECISION-001: Documentation-Aware Workflow

## Problem

AMIII is both a software project and a learning project. If implementation moves too quickly without documentation, future contributors will lose the reasoning behind decisions.

## Options Considered

- Strict documentation-first for all work.
- Code-first with no documentation requirement.
- Documentation-aware workflow with a fast-build exception.

## Chosen Option

Use documentation-aware development. Documentation-first remains the default, but small prototypes, fixes, scaffolding, and obvious implementation steps may be built first if documentation is updated before the session is considered complete.

## Reasoning

This keeps momentum while honoring the constitution's maintainability and teaching goals.

## Tradeoffs

- Requires discipline to update docs after fast implementation.
- Lets small improvements move faster.

## Future Impact

Major architecture changes still need decision records before or during implementation.

