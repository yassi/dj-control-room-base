from django.conf import settings
from django.templatetags.static import static
from django.utils.html import format_html, mark_safe

_CSS_DEFAULTS = {
    "LOAD_DEFAULT_CSS": True,
    "EXTRA_CSS": [],
}


def get_panel_settings(settings_key: str, defaults: dict | None = None) -> dict:
    """
    Merge user-defined settings (from Django settings) with provided defaults.

    :param settings_key: The Django settings attribute name, e.g. "DJ_REDIS_PANEL_SETTINGS"
    :param defaults: Dict of default values. Falls back to CSS defaults if not provided.
    """
    effective_defaults = defaults if defaults is not None else _CSS_DEFAULTS
    user = getattr(settings, settings_key, None) or {}
    return {**effective_defaults, **user}


def build_css_links(extra_css: list[str]) -> str:
    """
    Render a list of CSS paths/URLs into safe HTML <link> tags.

    Absolute URLs (http/https/protocol-relative) are used as-is;
    everything else is resolved through Django's static file system.
    """
    links = []
    for path in extra_css:
        url = path if path.startswith(("http://", "https://", "//")) else static(path)
        links.append(format_html('<link rel="stylesheet" href="{}">', url))
    return mark_safe("\n".join(links))


def build_css_context(
    settings_key: str,
    *,
    defaults: dict | None = None,
    load_key: str = "dj_cr_load_default_css",
    extra_key: str = "dj_cr_extra_css",
) -> dict:
    """
    Build the template context dict for CSS injection.

    :param settings_key: The Django settings attribute name for the panel.
    :param defaults: Panel-defined defaults. Falls back to _CSS_DEFAULTS if not provided.
    :param load_key: Template context key for the LOAD_DEFAULT_CSS boolean.
    :param extra_key: Template context key for the rendered <link> tags string.
    """
    cfg = get_panel_settings(settings_key, defaults=defaults)
    return {
        load_key: bool(cfg["LOAD_DEFAULT_CSS"]),
        extra_key: build_css_links(list(cfg["EXTRA_CSS"])),
    }
