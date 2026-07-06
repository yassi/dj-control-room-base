from dj_control_room_base.core.panel_tool import (
    PanelToolContext,
    PanelToolResult,
    ToolRegistry,
)

registry = ToolRegistry()


@registry.register(
    name="get_resolved_settings",
    scope="design-system",
    description=(
        "Returns the current resolved settings for this panel, "
        "including built-in defaults and any project overrides."
    ),
    input_schema={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
)
def handle_get_resolved_settings(ctx: PanelToolContext) -> PanelToolResult:
    """Return the current resolved settings for this panel."""
    settings = ctx.config.get_settings()
    return PanelToolResult(
        success=True,
        message="Resolved settings for the dj-control-room-base panel.",
        data=settings,
    )


@registry.register(
    name="get_design_system_url",
    scope="design-system",
    description="Returns the URL to the shared design system CSS file.",
    input_schema={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
)
def handle_get_design_system_url(ctx: PanelToolContext) -> PanelToolResult:
    """Return the URL to the shared design system CSS file."""
    from django.templatetags.static import static

    url = static("dj_control_room_base/css/design-system.css")
    return PanelToolResult(
        success=True,
        message="URL to the shared design system CSS.",
        data={"url": url},
    )
