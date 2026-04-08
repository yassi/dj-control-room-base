from django.conf import settings as django_settings
from django.contrib import admin
from django.http import HttpRequest
from django.templatetags.static import static
from django.utils.html import format_html, mark_safe


class PanelConfig:
    """
    Binds a panel's settings key and defaults into a single reusable object.

    Instantiate once in the panel's conf.py, then use the instance methods
    in views and elsewhere — no need to pass settings_key or defaults at
    every call site.

    Example::

        # myapp/conf.py
        from dj_control_room_base.core import PanelConfig

        panel_config = PanelConfig(
            settings_key="DJ_MY_PANEL_SETTINGS",
            defaults={"LOAD_DEFAULT_CSS": True, "EXTRA_CSS": []},
        )

        # myapp/views.py
        from myapp.conf import panel_config

        context = panel_config.get_context(request, title="My Panel")
    """

    def __init__(self, settings_key: str, defaults: dict | None = None) -> None:
        self.settings_key = settings_key
        self.defaults = defaults or {}

    def get_settings(self) -> dict:
        """Return merged panel settings (user overrides applied over defaults)."""
        user = getattr(django_settings, self.settings_key, None) or {}
        return {**self.defaults, **user}

    def get_css_context(self) -> dict:
        """Return the CSS injection context dict for use in templates."""
        cfg = self.get_settings()
        links = []
        for path in cfg.get("EXTRA_CSS", []):
            url = path if path.startswith(("http://", "https://", "//")) else static(path)
            links.append(format_html('<link rel="stylesheet" href="{}">', url))
        return {
            "dj_cr_load_default_css": bool(cfg.get("LOAD_DEFAULT_CSS", True)),
            "dj_cr_extra_css": mark_safe("\n".join(links)),
        }

    def get_context(self, request: HttpRequest, **extra) -> dict:
        """
        Build a full template context for a panel view.

        Includes the Django admin context, CSS injection, and any extra
        key/value pairs passed as keyword arguments (e.g. title="My Panel").
        """
        context = admin.site.each_context(request)
        context.update(self.get_css_context())
        context.update(extra)
        return context
