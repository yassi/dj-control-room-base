from dj_control_room_base.core import PanelConfig

from dj_control_room_base.tools import registry as tool_registry

panel_config = PanelConfig(
    settings_key="DJ_CONTROL_ROOM_BASE_SETTINGS",
    defaults={
        "LOAD_DEFAULT_CSS": True,
        "EXTRA_CSS": [],
    },
    tools=tool_registry.tools,
)
