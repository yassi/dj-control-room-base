"""
DJ Control Room panel plugin for dj-control-room-base.

Registers this package with the hub via the entry point defined in
``pyproject.toml`` under ``[project.entry-points."dj_control_room.panels"]``.
"""

from dj_control_room_base.core import PanelPlugin


class DJControlRoomBasePanel(PanelPlugin):
    name = "DJ Control Room Base"
    description = "Core framework for Django Control Room panels"
    icon = "database"

    app_name = "dj_control_room_base"
    docs_url = "https://github.com/django-control-room/dj-control-room-base"
    pypi_url = "https://pypi.org/project/dj-control-room-base/"

    def get_config(self):
        from .conf import panel_config

        return panel_config
