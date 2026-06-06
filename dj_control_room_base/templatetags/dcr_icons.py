"""
Template tags for rendering DJ Control Room panel icons.

Two tags are provided:

``dcr_icon`` — renders either an inline ``<svg>`` or an ``<img>``, depending
on whether ``key`` is a built-in icon name or an image URL/path::

    {% load dcr_icons %}

    {# Built-in icon — emits <svg> #}
    {% dcr_icon "database" %}
    {% dcr_icon panel.icon "dcr-panel-card__icon" %}

    {# Image — emits <img> (for custom logos, etc.) #}
    {# Relative static path — resolved via Django staticfiles at render time     #}
    {# File lives at: <app>/static/my_panel/images/logo.png                      #}
    {% dcr_icon "my_panel/images/logo.png" "dcr-panel-card__icon" %}
    {# Absolute URL — used as-is #}
    {% dcr_icon "https://cdn.example.com/logo.png" "dcr-panel-card__icon" %}

``dcr_icon_paths`` — inner path content only, for composing into an existing
``<svg>`` element where you control the ``viewBox`` and attributes yourself::

    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"
         fill="none" stroke="currentColor" stroke-width="1.5"
         stroke-linecap="round" stroke-linejoin="round">
      {% dcr_icon_paths "radio" %}
    </svg>

``ICONS`` maps each key to the raw inner SVG content (no ``<svg>`` wrapper,
no ``viewBox``).  Add new icons here; the design-guide gallery picks them up
automatically.  Do not include ``<svg>``, ``class``, ``width``, or ``height``
attributes in the stored strings.
"""

from django.template import Library
from django.templatetags.static import static as _static_url
from django.utils.safestring import mark_safe

register = Library()

_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg")


def _is_image(value: str) -> bool:
    """Return True if *value* looks like an image rather than a built-in icon key."""
    return (
        value.startswith(("http://", "https://", "/"))
        or any(value.endswith(ext) for ext in _IMAGE_EXTENSIONS)
    )

_SVG_ATTRS = (
    'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"'
)

# Inner path content only — no <svg> wrapper.
ICONS: dict[str, str] = {
    "database": (
        '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
        '<path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/>'
        '<path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/>'
    ),
    "layers": (
        '<polygon points="12 2 2 7 12 12 22 7 12 2"/>'
        '<polyline points="2 17 12 22 22 17"/>'
        '<polyline points="2 12 12 17 22 12"/>'
    ),
    "chart": (
        '<line x1="18" y1="20" x2="18" y2="10"/>'
        '<line x1="12" y1="20" x2="12" y2="4"/>'
        '<line x1="6" y1="20" x2="6" y2="14"/>'
    ),
    "link": (
        '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>'
        '<path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>'
    ),
    "radio": (
        '<circle cx="12" cy="12" r="2"/>'
        '<path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/>'
    ),
    "alert": (
        '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/>'
        '<line x1="12" y1="17" x2="12.01" y2="17"/>'
    ),
    "cog": (
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>'
    ),
    # Generic fallback — also available as an explicit key.
    "default": (
        '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>'
        '<line x1="3" y1="9" x2="21" y2="9"/>'
        '<line x1="9" y1="21" x2="9" y2="9"/>'
    ),
}


@register.simple_tag
def dcr_icon(key: str, css_class: str = "") -> str:
    """
    Render a panel icon as an inline ``<svg>`` or an ``<img>``.

    If *key* looks like an image (ends with a known extension, or starts with
    ``http://``, ``https://``, or ``/``) an ``<img>`` element is returned.
    Otherwise *key* is treated as a built-in icon name and an inline ``<svg>``
    is returned; unknown keys fall back to the ``"default"`` grid icon.

    Image resolution rules:

    - **Relative static path** (e.g. ``"my_panel/images/logo.png"``) —
      resolved through Django's staticfiles system using ``static()``.  Place
      the file at ``<app>/static/my_panel/images/logo.png`` and Django will
      return the correct URL regardless of ``STATIC_URL`` or CDN settings.
    - **Absolute URL** (starts with ``http://``, ``https://``, or ``/``) —
      used as-is.

    Args:
        key: Built-in icon key **or** an image path/URL.
        css_class: Space-separated CSS class(es) added to the element.

    Returns:
        Mark-safe HTML string.
    """
    class_attr = f' class="{css_class}"' if css_class else ""
    if _is_image(key):
        src = key if key.startswith(("http://", "https://", "/")) else _static_url(key)
        return mark_safe(f'<img src="{src}" alt=""{class_attr}>')
    content = ICONS.get(key, ICONS["default"])
    return mark_safe(f"<svg {_SVG_ATTRS}{class_attr}>{content}</svg>")


@register.simple_tag
def dcr_icon_paths(key: str) -> str:
    """
    Render the raw inner path content of an icon, without any ``<svg>`` wrapper.

    Use this when composing icons into an existing ``<svg>`` element where you
    control the ``viewBox`` and attributes yourself::

        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"
             fill="none" stroke="currentColor" stroke-width="1.5"
             stroke-linecap="round" stroke-linejoin="round">
          {% dcr_icon_paths "radio" %}
        </svg>

    Args:
        key: Icon key.  Unknown keys fall back to ``"default"``.

    Returns:
        Mark-safe inner SVG path content string (no ``<svg>`` wrapper).
    """
    return mark_safe(ICONS.get(key, ICONS["default"]))
