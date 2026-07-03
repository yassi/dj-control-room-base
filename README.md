[![Django Control Room Panel](https://img.shields.io/badge/Django%20Control%20Room-Panel-0c4b33?logo=django)](https://github.com/yassi/dj-control-room)
[![Tests](https://github.com/yassi/dj-control-room-base/actions/workflows/test.yml/badge.svg)](https://github.com/yassi/dj-control-room-base/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/yassi/dj-control-room-base/branch/main/graph/badge.svg)](https://codecov.io/gh/yassi/dj-control-room-base)
[![PyPI version](https://badge.fury.io/py/dj-control-room-base.svg)](https://badge.fury.io/py/dj-control-room-base)
[![Python versions](https://img.shields.io/pypi/pyversions/dj-control-room-base.svg)](https://pypi.org/project/dj-control-room-base/)
[![Downloads](https://img.shields.io/pypi/dm/dj-control-room-base.svg)](https://pypi.org/project/dj-control-room-base/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

# dj-control-room-base

![dj-control-room-base - a core library for creating DCR panels](https://raw.githubusercontent.com/yassi/dj-control-room-base/main/images/dj-control-room-base.png)



**dj-control-room-base** is a core library for [Django Control Room](https://github.com/yassi/dj-control-room) panels. It provides the shared primitives that every panel needs: settings management, CSS injection, permission enforcement, admin sidebar integration, template context helpers, and MCP-style panel tools.

**Official Django Control Room panels** ship with this package as a dependency and build on these APIs rather than reimplementing them panel by panel.

**Optionally**, the package can also be mounted as a full panel in its own right: it ships a bundled design system reference UI and example patterns that are useful when building or theming new panels.

- **Official site:** [djangocontrolroom.com](https://djangocontrolroom.com)
- **Control Room app:** [dj-control-room](https://github.com/yassi/dj-control-room)
- **Docs:** [yassi.github.io/dj-control-room-base](https://yassi.github.io/dj-control-room-base/)

## What this library provides

### Centralized CSS and permissions

The main value of this library is that it centralizes the settings every panel would otherwise duplicate independently. A single `PanelConfig` object, instantiated once in a panel's `conf.py`, handles:

- **CSS injection** - whether to load the shared design-system bundle, and any additional stylesheets, resolved and injected into template context automatically
- **Permission enforcement** - staff checks, optional superuser-only restriction, Django group allow lists, and per-view scope overrides, all driven from the same merged settings dict
- **Settings merging** - panel-level defaults, hub overrides from `dj-control-room`, and project-level settings are merged in a defined precedence order so each layer can override only what it needs

Panel authors who use `PanelConfig` get all of this for free. See [CSS and permissions](#css-and-permissions) below for the full reference.

### Admin sidebar integration

`PanelPlaceholderModel` and `BasePanelAdmin` give any panel a Django admin sidebar entry that redirects to the panel's main view, with no writable actions, no migrations, and automatic respect for the same permission rules configured on `PanelConfig`.

### Template context helpers

`panel_config.get_context(request, title="...")` returns a fully-prepared context dict that includes the standard Django admin context, CSS injection variables, and any extra kwargs you pass. No manual assembly required.

### Entry-point discovery and `PanelPlugin`

Panels register themselves with Control Room via a `pyproject.toml` entry point under `dj_control_room.panels`. The entry point points to a subclass of `PanelPlugin` (from `dj_control_room_base.core`), which carries the panel's identity metadata (name, description, icon, URLs) and wires back to the panel's `PanelConfig` via `get_config()`.

This library ships both the `PanelPlugin` base class and its own concrete implementation in `panel.py` as a reference.

The only runtime dependency is Django. `dj-control-room` is optional and only needed for the centralized hub dashboard.

### Panel tools

`PanelConfig` accepts an optional `tools` list of `PanelTool` instances. Each tool carries a name, a scope (reusing the same permission system as views), a human-readable description, a JSON Schema for its inputs, and a handler callable. When installed panels expose tools, the `dj-control-room` hub aggregates them across all panels, filters by the current user's permissions at request time, and dispatches calls through a unified endpoint — suitable for AI agent integrations and an in-admin chat experience with no per-panel HTTP wiring required.

## Screenshots

**Django admin** - the placeholder model registers an app entry that redirects to the panel, with no extra migrations required:

![Django admin home showing the DJ Control Room Base sidebar entry](https://raw.githubusercontent.com/yassi/dj-control-room-base/main/images/admin_home.png)

**The panel UI** - the bundled design system reference view, accessible at `/admin/dj-control-room-base/`:

![DJ Control Room Base design system panel view](https://raw.githubusercontent.com/yassi/dj-control-room-base/main/images/dcr-base-design-system.png)

**django-unfold support** - panels adopt the host site's accent and neutral colors via the bundled [theme adapter](#theme-adapters):

![Django Control Room running with the django-unfold admin theme](https://raw.githubusercontent.com/yassi/dj-control-room-base/main/images/dcr-base-unfold.png)

## Requirements

- Python 3.9+
- Django 4.2+ (tested in CI across Django 4.2, 5.2, and 6.0)


## Project layout

```
dj-control-room-base/
├── dj_control_room_base/
│   ├── core/              # PanelPlugin, PanelConfig, PanelTool, BasePanelAdmin, PanelPlaceholderModel
│   ├── templates/         # Panel templates
│   ├── static/            # Design system CSS and assets
│   ├── conf.py            # PanelConfig instance (with example tools)
│   ├── panel.py           # Control Room entry-point panel class
│   ├── tools.py           # Example tool handler functions
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── models.py          # Placeholder model for admin sidebar
├── example_project/       # Runnable demo + pytest settings
├── tests/
├── mkdocs.yml             # Documentation site
└── requirements.txt       # Dev / demo deps (includes dj-control-room)
```


## Quick start

```bash
pip install dj-control-room-base
```

```python
# settings.py
INSTALLED_APPS = [
    ...
    "dj_control_room_base",
]
```

```python
# urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/dj-control-room-base/", include("dj_control_room_base.urls")),
    path("admin/", admin.site.urls),
]
```

```bash
python manage.py migrate
python manage.py runserver
```

Open `/admin/` and sign in. A **DJ CONTROL ROOM BASE** entry appears in the sidebar and links to the panel at `/admin/dj-control-room-base/`.

See the [full documentation](https://yassi.github.io/dj-control-room-base/) for installation options, configuration reference, and a guide for building your own panel on this library.

## Django Control Room dashboard

1. Add `dj_control_room` to `INSTALLED_APPS` (with `dj_control_room_base`).
2. Include `path("admin/dj-control-room/", include("dj_control_room.urls"))` as above.
3. Open `/admin/dj-control-room/` to see registered panels (this package advertises itself via the `dj_control_room.panels` entry point).

The panel's identity (name, description, icon, docs/PyPI links) is declared in `dj_control_room_base/panel.py` as a `PanelPlugin` subclass. Build your own panel package the same way.


## CSS and permissions

`PanelConfig` is the central object that every panel built on this library uses. Instantiate it once in `conf.py` with a settings key and panel-level defaults, then call its helpers from views, templates, and the admin class. The same config object drives CSS injection, permission checks, and the full template context.

### Settings merge order

Settings are resolved fresh on every call so that runtime changes (e.g. from the Control Room hub) are always picked up. The merge order is, from lowest to highest priority:

1. **Built-in defaults** (`PANEL_BUILTIN_DEFAULTS` in `core/panel_config.py`) - CSS and permission keys that every panel gets automatically, even if the panel author never declares them.
2. **Panel defaults** - the `defaults` dict passed to `PanelConfig(...)` in the panel's own `conf.py`.
3. **Hub overrides** - injected at runtime by `dj-control-room` via `apply_override_settings()` when the hub is installed. Lets the hub enforce global CSS or permission policies across all panels from a single place.
4. **Project settings** - the dict at `settings.DJ_<PANEL>_SETTINGS` in the consuming Django project. These win over everything, so a project can always opt out of hub defaults.

The result is that panel authors declare a minimal `defaults`, project owners override only what they need, and the hub can push cross-panel policy without touching individual panel settings files.

### CSS settings

| Key | Type | Default | Effect |
|---|---|---|---|
| `LOAD_DEFAULT_CSS` | `bool` | `True` | Loads the shared `design-system.css` bundle from this package. Set to `False` if the hub or a parent template already loads it. |
| `EXTRA_CSS` | `list[str]` | `[]` | Additional stylesheets to inject. Relative paths are resolved through Django's `staticfiles`; absolute URLs (`http://`, `https://`, `//`) are used as-is. |

In a view, call `panel_config.get_context(request, title="My Panel")` to get a context dict that already contains `dj_cr_load_default_css` and `dj_cr_extra_css` alongside the standard Django admin context. Templates use these to inject the right `<link>` tags without any per-view wiring.

### Theme adapters

For admin skins that don't match the classic Django admin palette, the package ships optional token-override stylesheets under `dj_control_room_base/css/themes/`. They're opt-in per panel via `EXTRA_CSS` - nothing loads automatically:

```python
DJ_MY_PANEL_SETTINGS = {
    "EXTRA_CSS": ["dj_control_room_base/css/themes/unfold.css"],
}
```

`themes/unfold.css` remaps DCR's accent/surface/border/muted tokens to [django-unfold](https://github.com/unfoldadmin/django-unfold)'s own CSS variables (`--color-primary-*`, `--color-base-*`, `--color-font-*`), so panels match the host site's configured brand color. See the [configuration docs](https://yassi.github.io/dj-control-room-base/configuration/#theme-adapters) for details.

### Permission settings

Panels built on this library follow a two-level permission model: a **panel-wide** policy, and optional **per-scope** overrides for individual views.

**Panel-wide keys** (apply to all views unless a scope overrides them):

| Key | Type | Default | Effect |
|---|---|---|---|
| `ALLOWED_GROUPS` | `list[str]` | `[]` | Django group names that may access the panel. Empty list means any staff user is allowed. |
| `REQUIRE_SUPERUSER` | `bool` | `False` | Restricts the panel to superusers only. |

**Per-view scopes** (`SCOPE_PERMISSIONS`):

A scope is a string label that matches the argument passed to `@panel_config.permission_required("my-scope")` on a view. Each scope entry accepts the same `ALLOWED_GROUPS` and `REQUIRE_SUPERUSER` keys and overrides the panel-wide values for that view only.

```python
"SCOPE_PERMISSIONS": {
    "reports": {"REQUIRE_SUPERUSER": True},     # only superusers
    "dashboard": {"ALLOWED_GROUPS": ["ops"]},   # ops group only
    "status": {},                               # inherits panel-wide policy
}
```

**Resolution rules** (applied in order):

1. The user must be **authenticated** and **staff**. Anonymous users are redirected to the Django admin login.
2. **Superusers** always pass (they bypass group checks, matching Django admin behaviour).
3. If `REQUIRE_SUPERUSER` is `True` for the resolved scope, non-superusers receive a 403.
4. If `ALLOWED_GROUPS` is non-empty, the user must belong to at least one of those groups (checked by name). An empty list skips the group check.

### Using it in a panel

```python
# myapp/conf.py
from dj_control_room_base.core import PanelConfig

panel_config = PanelConfig(
    settings_key="DJ_MY_PANEL_SETTINGS",
    defaults={
        "LOAD_DEFAULT_CSS": True,
        "EXTRA_CSS": [],
    },
)

# myapp/views.py
from .conf import panel_config

@panel_config.permission_required("dashboard")
def dashboard(request):
    context = panel_config.get_context(request, title="Dashboard")
    return render(request, "mypanel/dashboard.html", context)
```

That is the entirety of the wiring. Permission enforcement, login redirect, CSS injection, and the Django admin context are all handled by the two `panel_config` calls.


## Building your own panel on this package

Import primitives from `dj_control_room_base.core`:

- **`PanelPlugin`** - Subclass in `panel.py` to declare your panel's identity (name, description, icon, URLs) and wire it to your `PanelConfig` via `get_config()`. Point the entry point at this subclass.
- **`PanelConfig`** - Instantiate in `conf.py` with your settings key, defaults, and optional `tools` list; use `get_context`, `permission_required`, and CSS helpers in views.
- **`PanelPlaceholderModel`** - Abstract `managed=False` base for a sidebar-only model.
- **`BasePanelAdmin`** - Redirect changelist to your `namespace:index` URL; set `panel_config` for aligned permissions.

From `dj_control_room_base.core.panel_tool`:

- **`PanelTool`** - Declare a tool with a name, scope, description, JSON Schema input definition, and handler callable.
- **`PanelToolContext`** - Passed to each handler at call time: carries `user`, `inputs`, and `config`.
- **`PanelToolResult`** - Returned by handlers: carries `success`, `message`, and a `data` dict.

Register with the hub via `pyproject.toml`:

```toml
[project.entry-points."dj_control_room.panels"]
my_panel = "my_panel.panel:MyPanel"
```

```python
# my_panel/panel.py
from dj_control_room_base.core import PanelPlugin

class MyPanel(PanelPlugin):
    name = "My Panel"
    description = "Does something useful"
    icon = "cog"

    def get_config(self):
        from .conf import panel_config
        return panel_config
```

To expose tools to the hub, add them to `PanelConfig` in `conf.py` and define handlers in a separate `tools.py` (use local imports inside handlers for anything that touches models):

```python
# my_panel/conf.py
from dj_control_room_base.core import PanelConfig
from dj_control_room_base.core.panel_tool import PanelTool
from my_panel.tools import handle_get_item

panel_config = PanelConfig(
    settings_key="DJ_MY_PANEL_SETTINGS",
    defaults={"LOAD_DEFAULT_CSS": True},
    tools=[
        PanelTool(
            name="get_item",
            scope="read",
            description="Fetch a single item by key.",
            input_schema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "The item key."},
                },
                "required": ["key"],
            },
            handler=handle_get_item,
        ),
    ],
)
```


## Development

Clone and install in editable mode with dev dependencies:

```bash
git clone https://github.com/yassi/dj-control-room-base.git
cd dj-control-room-base
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
make install                # pip install -r requirements.txt && pip install -e .
```

Run tests locally (uses SQLite by default via `example_project` settings):

```bash
make test_local
# or: python -m pytest tests/ -v
```

Coverage:

```bash
make test_coverage
```

Docker Compose provides a **dev** container (app on port 8000) and optional **Postgres**. From the repo root:

```bash
make docker_up
make docker_shell    # working directory: /app/example_project
```

Inside the container you can run `python manage.py runserver 0.0.0.0:8000` or pytest. For Postgres-backed runs, set `DB_ENGINE=postgresql` and point host/user/password at the `postgres` service.

Documentation:

```bash
make docs          # mkdocs build
make docs_serve    # local preview
```


## License

MIT. See [LICENSE](LICENSE).
