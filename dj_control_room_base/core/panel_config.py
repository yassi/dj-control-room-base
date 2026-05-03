import functools

from django.conf import settings as django_settings
from django.contrib import admin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html, mark_safe


# Default keys merged before panel ``defaults`` (see ``get_settings``). Panels omit
# these in ``conf.py`` and still get consistent behaviour across CSS and permission.
PANEL_BUILTIN_DEFAULTS: dict[str, object] = {
    "LOAD_DEFAULT_CSS": True,
    "EXTRA_CSS": [],
    "ALLOWED_GROUPS": [],
    "REQUIRE_SUPERUSER": False,
    "SCOPE_PERMISSIONS": {},
}


class PanelConfig:
    """
    Binds a panel's settings key and defaults into a single reusable object.

    Instantiate once in the panel's conf.py, then use the instance methods
    in views and elsewhere — no need to pass settings_key or defaults at
    every call site.

    Builtin defaults (:data:`PANEL_BUILTIN_DEFAULTS`) are merged beneath
    the panel ``defaults``, then hub overrides and project Django settings.

    Permission checks use the same merged mapping as ``get_settings()`` on each call.

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

        # This is used by the dj-control-room package to override settings for the panel
        # in order to provide a consistent interface for all panels. It is not needed
        # when using panels standalone.
        self._override_settings = {}

    def apply_override_settings(self, settings: dict) -> None:
        """Apply the DJ Control Room override settings to the panel config."""
        self._override_settings = settings

    def get_settings(self, key: str | None = None) -> dict:
        """Return merged panel settings (defined settings overrides applied over defaults)."""
        # settings defined for the panel in the consuming project's app settings
        defined_settings = getattr(django_settings, self.settings_key, None) or {}

        # combine settings and follow the order of precedence
        # 0. builtins — package-wide defaults including permission keys (see ``PANEL_BUILTIN_DEFAULTS``)
        # 1. defaults — settings defined in a panel's conf.py
        # 2. override settings — settings defined in the dj-control-room package like
        # DJ_CONTROL_ROOM_SETTINGS = {
        #     "LOAD_DEFAULT_CSS": False,
        #     "EXTRA_CSS": ["dj_control_room_base/css/overrides.css"],
        #     "panels": {
        #         "dj_redis_panel": {
        #             "ALLOW_OPTION": True,
        #         }
        #     }
        # }
        # 3. defined settings — settings defined in the consuming project's app settings
        # DJ_REDIS_PANEL_SETTINGS = {
        #     "LOAD_DEFAULT_CSS": False,
        #     "ALLOW_OPTION": True,
        # }
        combined_settings = {
            **PANEL_BUILTIN_DEFAULTS,
            **self.defaults,
            **self._override_settings,
            **defined_settings,
        }
        if key is not None:
            return combined_settings.get(key)
        return combined_settings

    def _resolve_permission_settings(self, scope: str | None = None) -> dict:
        merged = self.get_settings()
        scope_map_raw = merged["SCOPE_PERMISSIONS"]
        scope_permissions = scope_map_raw if isinstance(scope_map_raw, dict) else {}
        panel_level = {
            "ALLOWED_GROUPS": merged["ALLOWED_GROUPS"],
            "REQUIRE_SUPERUSER": merged["REQUIRE_SUPERUSER"],
        }
        if scope is None:
            return panel_level
        scope_overrides = scope_permissions.get(scope, {})
        if not isinstance(scope_overrides, dict):
            scope_overrides = {}
        return {**panel_level, **scope_overrides}

    def has_permission(self, request: HttpRequest, scope: str | None = None) -> bool:
        """Return True if the request's user may access this panel or scope."""
        if not request.user.is_staff:
            return False
        settings = self._resolve_permission_settings(scope)
        if settings["REQUIRE_SUPERUSER"]:
            return request.user.is_superuser
        allowed_groups = settings["ALLOWED_GROUPS"]
        allowed = allowed_groups if isinstance(allowed_groups, (list, tuple)) else ()
        if allowed:
            return request.user.groups.filter(name__in=allowed).exists()
        return True

    def permission_required(self, scope: str | None = None):
        """Decorator: redirect anonymous users to admin login; 403 otherwise if unauthorised."""
        def decorator(view_func):
            @functools.wraps(view_func)
            def wrapper(request, *args, **kwargs):
                if not request.user.is_authenticated:
                    return redirect_to_login(
                        request.get_full_path(),
                        login_url=reverse("admin:login"),
                    )
                if not self.has_permission(request, scope):
                    raise PermissionDenied
                return view_func(request, *args, **kwargs)
            return wrapper
        return decorator

    def get_css_context(self) -> dict:
        """Return the CSS injection context dict for use in templates."""
        settings = self.get_settings()
        links = []
        for path in settings.get("EXTRA_CSS", []):
            url = (
                path if path.startswith(("http://", "https://", "//")) else static(path)
            )
            links.append(format_html('<link rel="stylesheet" href="{}">', url))
        return {
            "dj_cr_load_default_css": bool(settings.get("LOAD_DEFAULT_CSS", True)),
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
