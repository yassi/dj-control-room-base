# Configuration

`dj_control_room_base` works out of the box with sensible defaults. Everything is optional - you only need to add settings when you want to change the default behavior.

The settings key for this panel is **`DJ_CONTROL_ROOM_BASE_SETTINGS`**.

```python
# settings.py
DJ_CONTROL_ROOM_BASE_SETTINGS = {
    "LOAD_DEFAULT_CSS": True,
    "EXTRA_CSS": [],
    "ALLOWED_GROUPS": [],
    "REQUIRE_SUPERUSER": False,
    "SCOPE_PERMISSIONS": {},
}
```

All keys shown above are the defaults. You only need to declare the keys you want to change.

---

## How settings are merged

Settings are resolved fresh on each request by merging four layers, from lowest to highest priority:

| Priority | Layer | Source |
|---|---|---|
| 1 (lowest) | Built-in defaults | `PANEL_BUILTIN_DEFAULTS` in `core/panel_config.py` |
| 2 | Panel defaults | `defaults={}` passed to `PanelConfig(...)` in `conf.py` |
| 3 | Hub overrides | Injected at runtime by `dj-control-room` when installed |
| 4 (highest) | Project settings | `DJ_CONTROL_ROOM_BASE_SETTINGS` in your Django settings file |

This layering means:

- **Panel authors** declare a minimal set of defaults for their panel. They never need to worry about the built-in keys.
- **The hub** can enforce cross-panel policies (e.g. disable the default CSS globally, restrict permissions) without touching individual panels.
- **Project owners** always win. Anything in `DJ_CONTROL_ROOM_BASE_SETTINGS` overrides everything else, so you can always opt out of hub defaults.

---

## CSS settings

### `LOAD_DEFAULT_CSS`

**Type:** `bool` | **Default:** `True`

Controls whether the shared `design-system.css` bundle shipped with this package is loaded in panel templates. When `True`, the bundle is injected automatically via the template context.

Set to `False` if:

- The Control Room hub already loads the design-system CSS globally and you want to avoid a double load.
- You are replacing the design system entirely with your own stylesheet.

```python
DJ_CONTROL_ROOM_BASE_SETTINGS = {
    "LOAD_DEFAULT_CSS": False,
}
```

### `EXTRA_CSS`

**Type:** `list[str]` | **Default:** `[]`

Additional stylesheets to inject after the default bundle (or after nothing, if `LOAD_DEFAULT_CSS` is `False`). Each entry can be either:

- A **Django static file path** (relative to `STATIC_ROOT`) - resolved through `staticfiles` at render time.
- An **absolute URL** starting with `http://`, `https://`, or `//` - used as-is.

```python
DJ_CONTROL_ROOM_BASE_SETTINGS = {
    "LOAD_DEFAULT_CSS": True,
    "EXTRA_CSS": [
        "my_panel/css/overrides.css",            # resolved via staticfiles
        "https://cdn.example.com/theme.css",     # used as-is
    ],
}
```

!!! note "How CSS reaches templates"
    `panel_config.get_context(request)` calls `get_css_context()` internally and merges the result into the template context. Templates receive two variables:

    - `dj_cr_load_default_css` - boolean, whether to render the design-system `<link>` tag
    - `dj_cr_extra_css` - pre-rendered `<link>` tag HTML for each `EXTRA_CSS` entry, marked safe

    If you are writing a panel template from scratch, extend `panel_base.html` (which handles these variables) or render them yourself.

### Theme adapters

The package ships optional token-override stylesheets under `dj_control_room_base/css/themes/` for admin skins that don't match the classic Django admin palette. These are **not loaded automatically** - add the one you need to `EXTRA_CSS` on each panel where you want it applied:

```python
DJ_MY_PANEL_SETTINGS = {
    "EXTRA_CSS": ["dj_control_room_base/css/themes/unfold.css"],
}
```

Currently available:

| File | For |
|---|---|
| `themes/unfold.css` | Projects using [django-unfold](https://github.com/unfoldadmin/django-unfold) as their admin skin. |
| `themes/jazzmin.css` | Projects using [django-jazzmin](https://github.com/farridav/django-jazzmin) as their admin skin. |

`themes/unfold.css` remaps a handful of `--dcr-*` tokens (accent color, surfaces, borders, muted text) to Unfold's own `--color-primary-*` / `--color-base-*` / `--color-font-*` CSS variables, so panels pick up the host site's configured brand color instead of DCR's classic-admin blue. It only touches tokens - never `dcr-*` component rules - and every override falls back to DCR's own default if the Unfold variable isn't present, so it's safe to load even if Unfold changes its internals in a future release. Semantic status colors (success/warning/danger/info) are left alone, since Unfold doesn't expose those as configurable brand colors.

`themes/jazzmin.css` follows the same approach for Jazzmin's Bootstrap 5 foundation, remapping the same set of tokens to `--bs-body-color`, `--bs-border-color`, `--bs-secondary-color`, `--bs-tertiary-bg`, `--bs-primary`, and `--bs-primary-bg-subtle` - so panels track whatever Bootswatch theme is configured via `JAZZMIN_UI_TWEAKS["theme"]` instead of hardcoding one palette. Same fallback safety and same scope (tokens only, no `dcr-*` component rules, semantic status colors untouched).

Both adapters rely on `design-system.css` already recognizing the host skin's dark-mode signal so the *default* DCR palette (not just the adapter's own overrides) switches correctly: Unfold toggles a plain `dark` class on `<html>`, while Jazzmin (via Bootstrap 5) sets `data-bs-theme="dark"` on `<html>`. Both are handled automatically - no extra configuration needed beyond loading the adapter's stylesheet.

Because this is opt-in per panel rather than hub-wide, each panel you want themed needs its own `EXTRA_CSS` entry for now.

![Django Control Room running with the django-unfold admin theme](https://raw.githubusercontent.com/django-control-room/dj-control-room-base/main/images/dcr-base-unfold.png)

You can also make your own theme adapters easily by following the `unfold.css` or
`jazzmin.css` examples. This works very well for any Tailwind CSS or Bootstrap
driven admin that exposes its palette as CSS custom properties.

---

## Permission settings

Panels built on this library use a two-level permission model: **panel-wide** defaults and optional **per-scope** overrides for individual views.

All permission checks require the user to be **authenticated and staff** as a baseline. Anonymous users are redirected to the Django admin login page.

### `ALLOWED_GROUPS`

**Type:** `list[str]` | **Default:** `[]`

A list of Django group names that are allowed to access the panel. The check uses group name matching.

- **Empty list (default):** any staff user can access the panel.
- **Non-empty list:** the user must belong to at least one of the named groups.

```python
DJ_CONTROL_ROOM_BASE_SETTINGS = {
    "ALLOWED_GROUPS": ["ops", "support"],
}
```

!!! note "Superusers bypass group checks"
    Superusers always pass, regardless of `ALLOWED_GROUPS`. This mirrors Django's own admin behavior.

### `REQUIRE_SUPERUSER`

**Type:** `bool` | **Default:** `False`

When `True`, only superusers can access the panel. Non-superuser staff receive a 403.

```python
DJ_CONTROL_ROOM_BASE_SETTINGS = {
    "REQUIRE_SUPERUSER": True,
}
```

---

## Scoped permissions

`SCOPE_PERMISSIONS` lets you set different permission rules for individual views, overriding the panel-wide policy for just that view.

A **scope** is a string label that matches the argument passed to `@panel_config.permission_required("my-scope")` on a view function. Each scope entry accepts the same `ALLOWED_GROUPS` and `REQUIRE_SUPERUSER` keys as the panel-wide settings.

```python
DJ_CONTROL_ROOM_BASE_SETTINGS = {
    # Panel-wide defaults (apply to any view not listed in SCOPE_PERMISSIONS)
    "ALLOWED_GROUPS": [],
    "REQUIRE_SUPERUSER": False,

    "SCOPE_PERMISSIONS": {
        # Only superusers can reach the design-system view
        "design-system": {
            "REQUIRE_SUPERUSER": True,
        },
        # Only the "editors" group can reach the examples view
        "examples": {
            "ALLOWED_GROUPS": ["editors"],
        },
    },
}
```

If a scope key is present but its dict is empty (`{}`), that view inherits the panel-wide `ALLOWED_GROUPS` and `REQUIRE_SUPERUSER` values exactly.

### Permission resolution order

For every request, permissions are resolved as follows:

1. **Not authenticated** - redirect to admin login.
2. **Not staff** - 403.
3. **Superuser** - always allowed (mirrors Django admin).
4. **`REQUIRE_SUPERUSER` is True** for the resolved scope - 403 for non-superusers.
5. **`ALLOWED_GROUPS` is non-empty** for the resolved scope - 403 if the user is not in any of those groups.
6. Otherwise - allowed.

---

## Full reference

All supported keys with their types and defaults:

| Key | Type | Default | Description |
|---|---|---|---|
| `LOAD_DEFAULT_CSS` | `bool` | `True` | Load the bundled `design-system.css`. |
| `EXTRA_CSS` | `list[str]` | `[]` | Extra stylesheets to inject (static paths or URLs). |
| `ALLOWED_GROUPS` | `list[str]` | `[]` | Group names allowed panel-wide. Empty means any staff. |
| `REQUIRE_SUPERUSER` | `bool` | `False` | Restrict panel to superusers only. |
| `SCOPE_PERMISSIONS` | `dict` | `{}` | Per-scope overrides for `ALLOWED_GROUPS` and `REQUIRE_SUPERUSER`. |
