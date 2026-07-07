from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class PanelTool:
    name: str
    scope: str
    description: str
    input_schema: dict
    handler: Callable


@dataclass
class PanelToolResult:
    success: bool
    message: str
    data: dict = field(default_factory=dict)


@dataclass
class PanelToolContext:
    user: Any
    inputs: dict
    config: Any  # PanelConfig — not imported here to avoid a circular dependency


class ToolRegistry:
    """
    Collects ``PanelTool`` definitions via a ``@registry.register(...)``
    decorator, so a tool's metadata lives directly above the handler function
    it describes instead of in a separate list that has to be kept in sync.

    Instantiate one per panel's ``tools.py`` module::

        # dj_my_panel/tools.py
        from dj_control_room_base.core.panel_tool import (
            PanelToolContext, PanelToolResult, ToolRegistry,
        )

        registry = ToolRegistry()

        @registry.register(
            name="get_item",
            scope="read",
            description="Fetch a single item by key.",
            input_schema={
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
            },
        )
        def handle_get_item(ctx: PanelToolContext) -> PanelToolResult:
            ...

    Then wire it into ``conf.py``::

        from .tools import registry as tool_registry

        panel_config = PanelConfig(..., tools=tool_registry.tools)

    The decorator only records metadata as a side effect — it returns the
    wrapped function unchanged, so handlers stay plain, directly callable
    functions (e.g. from tests).
    """

    def __init__(self) -> None:
        self._tools: list["PanelTool"] = []

    def register(
        self,
        *,
        name: str,
        scope: str,
        description: str,
        input_schema: dict,
    ) -> Callable[[Callable], Callable]:
        """Decorator: wraps a handler's metadata into a PanelTool and records it."""

        def decorator(handler: Callable) -> Callable:
            if any(t.name == name for t in self._tools):
                raise ValueError(
                    f"A tool named '{name}' is already registered on this ToolRegistry."
                )
            self._tools.append(
                PanelTool(
                    name=name,
                    scope=scope,
                    description=description,
                    input_schema=input_schema,
                    handler=handler,
                )
            )
            return handler

        return decorator

    @property
    def tools(self) -> list["PanelTool"]:
        """The PanelTool definitions collected so far, in registration order."""
        return list(self._tools)

    def __len__(self) -> int:
        return len(self._tools)

    def __iter__(self):
        return iter(self.tools)
