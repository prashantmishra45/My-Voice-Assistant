"""Confirmation helpers for risky AMIII actions."""

from __future__ import annotations

from collections.abc import Callable


class ConfirmationService:
    """Ask the user before performing risky actions."""

    def __init__(
        self,
        input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print,
    ) -> None:
        self._input = input_func
        self._output = output_func

    def confirm(self, action_description: str) -> bool:
        self._output(f"Confirmation required: {action_description}")
        answer = self._input("Proceed? Type 'yes' to continue: ")
        return answer.strip().lower() == "yes"

