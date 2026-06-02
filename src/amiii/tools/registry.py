"""Simple registry for future AMIII tools."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


ToolCallable = Callable[..., Any]


@dataclass(frozen=True)
class RegisteredTool:
    name: str
    description: str
    handler: ToolCallable
    requires_confirmation: bool = False


class ToolRegistry:
    """Register and retrieve future assistant tools."""

    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(self, tool: RegisteredTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> RegisteredTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Tool not registered: {name}") from exc

    def list_tools(self) -> tuple[RegisteredTool, ...]:
        return tuple(self._tools.values())

