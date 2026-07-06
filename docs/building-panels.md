# Building Panels

This guide is for panel authors who want to build a new Django Control Room panel using `dj-control-room-base` as the core library.

By building on this library you get CSS injection, permission enforcement, admin sidebar integration, and template context helpers for free - without reimplementing them per panel.

---

## Prerequisites

Your panel will be a standard Django app distributed as a Python package. It needs to:

1. Declare `dj-control-room-base` as a dependency in `pyproject.toml`.
2. Register itself with Control Room via an entry point.
3. Use `PanelConfig` from `dj_control_room_base.core` in its own `conf.py`.

---

## 1. Declare the dependency

```toml
# pyproject.toml
[project]
name = "dj-my-panel"
dependencies = [
    "Django>=4.2",
    "dj-control-room-base>=0.1.0",
]
```

---

## 2. Register the entry point

Control Room discovers installed panels by scanning the `dj_control_room.panels` entry point group. Add one entry that points to your panel class:

```toml
# pyproject.toml
[project.entry-points."dj_control_room.panels"]
dj_my_panel = "dj_my_panel.panel:MyPanel"
```

---

## 3. Create the panel class

The panel class is how your package introduces itself to the hub. It carries the metadata Control Room displays on the dashboard and provides the hook for returning your `PanelConfig`. Subclass `PanelPlugin` from `dj_control_room_base.core`:

```python
# dj_my_panel/panel.py
from dj_control_room_base.core import PanelPlugin


class MyPanel(PanelPlugin):
    name = "My Panel"
    description = "A short description of what this panel does."
    icon = "database"           # icon name from the design system
    app_name = "dj_my_panel"   # must match the app label in INSTALLED_APPS
    docs_url = "https://github.com/yourname/dj-my-panel"
    pypi_url = "https://pypi.org/project/dj-my-panel/"

    def get_config(self):
        from .conf import panel_config
        return panel_config
```

`get_config()` uses a local import so that `conf.py` is not pulled into the module namespace during entry-point discovery (which happens before Django is fully set up). The `get_url_name()` method defaults to `"index"` and only needs to be overridden if your main view uses a different name.

---

## 4. Create `conf.py`

Instantiate `PanelConfig` once. This object is the single source of truth for your panel's settings, CSS, and permission logic.

```python
# dj_my_panel/conf.py
from dj_control_room_base.core import PanelConfig

panel_config = PanelConfig(
    settings_key="DJ_MY_PANEL_SETTINGS",
    defaults={
        "LOAD_DEFAULT_CSS": True,
        "EXTRA_CSS": [],
    },
)
```

`settings_key` is the Django settings variable that project owners use to configure your panel. The `defaults` dict is the fallback when the project hasn't set that variable.

You do not need to declare `ALLOWED_GROUPS`, `REQUIRE_SUPERUSER`, or `SCOPE_PERMISSIONS` in `defaults` - those are provided automatically by the built-in defaults (`PANEL_BUILTIN_DEFAULTS`).

---

## 5. Write views

Use `@panel_config.permission_required("scope-name")` to protect views and `panel_config.get_context(request, ...)` to build the template context. Both use the same merged settings, so they stay in sync automatically.

```python
# dj_my_panel/views.py
from django.shortcuts import render
from .conf import panel_config


@panel_config.permission_required("dashboard")
def dashboard(request):
    context = panel_config.get_context(request, title="My Panel")
    return render(request, "dj_my_panel/dashboard.html", context)


@panel_config.permission_required("detail")
def detail(request, pk):
    context = panel_config.get_context(request, title="Detail View")
    return render(request, "dj_my_panel/detail.html", context)
```

The scope string (`"dashboard"`, `"detail"`) becomes a key in `SCOPE_PERMISSIONS` that project owners can override without touching your code:

```python
# In the project's settings.py
DJ_MY_PANEL_SETTINGS = {
    "SCOPE_PERMISSIONS": {
        "dashboard": {"ALLOWED_GROUPS": ["ops"]},
        "detail": {"REQUIRE_SUPERUSER": True},
    }
}
```

---

## 6. Register URLs

```python
# dj_my_panel/urls.py
from django.urls import path
from . import views

app_name = "dj_my_panel"

urlpatterns = [
    path("", views.dashboard, name="index"),
    path("<int:pk>/", views.detail, name="detail"),
]
```

The `app_name` must match `panel.app_name` and the `app_name` in `AppConfig`.

---

## 7. Add the admin sidebar entry

Use `PanelPlaceholderModel` and `BasePanelAdmin` to register a Django admin sidebar entry that redirects to your panel's main view. No database table is created.

```python
# dj_my_panel/models.py
from dj_control_room_base.core import PanelPlaceholderModel

class MyPanelPlaceholder(PanelPlaceholderModel):
    class Meta(PanelPlaceholderModel.Meta):
        verbose_name = "My Panel"
        verbose_name_plural = "My Panel"
```

```python
# dj_my_panel/admin.py
from django.contrib import admin
from dj_control_room_base.core import BasePanelAdmin
from .conf import panel_config
from .models import MyPanelPlaceholder


@admin.register(MyPanelPlaceholder)
class MyPanelAdmin(BasePanelAdmin):
    redirect_url_name = "dj_my_panel:index"
    panel_config = panel_config
```

Attaching `panel_config` to `BasePanelAdmin` means the sidebar entry is only visible to users who have permission to access the panel. The same permission rules configured in `DJ_MY_PANEL_SETTINGS` apply to the admin entry automatically.

---

## 8. Create templates

Extend `panel_base.html` (shipped with this library) to inherit the design system CSS wiring and Django admin chrome:

```html
{% extends "dj_control_room_base/panel_base.html" %}

{% block content %}
  <div class="dcr-page-header">
    <h1 class="dcr-page-header__title">My Panel</h1>
  </div>
  <!-- your panel content -->
{% endblock %}
```

The base template automatically handles `dj_cr_load_default_css` and `dj_cr_extra_css` from the context, so CSS injection requires no additional template code.

---

## Panel tools

Panel tools are optional, structured callables that the `dj-control-room` hub can aggregate across all installed panels and expose through a unified API. They are designed to power AI agent integrations (where an LLM calls tools on your behalf) and an in-admin chat experience, but they are generic enough to be used in any context that needs a structured, permission-aware callable.

Tools reuse the same scope-based permission system as views — no separate permission wiring is needed.

### Tool primitives

All four are importable from `dj_control_room_base.core.panel_tool`:

**`PanelTool`** — the tool definition. You'll rarely construct this directly (see `ToolRegistry` below), but it's what ends up on `PanelConfig.tools`:

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Short identifier for this tool, unique within the panel (e.g. `"get_key"`). The hub namespaces it as `<panel_id>__<name>`. |
| `scope` | `str` | Permission scope. Reuses the same scope strings as `@panel_config.permission_required(scope)`. |
| `description` | `str` | Human-readable description of what the tool does. Shown to LLMs and in the hub tool listing. |
| `input_schema` | `dict` | [JSON Schema](https://json-schema.org) object describing the tool's input arguments. Tools that take no arguments should use `{"type": "object", "properties": {}}`. |
| `handler` | `Callable` | A function that receives a `PanelToolContext` and returns a `PanelToolResult`. |

**`PanelToolContext`** — passed to the handler at call time:

| Field | Type | Description |
|---|---|---|
| `user` | `Any` | The Django `User` object of the caller. |
| `inputs` | `dict` | The validated input arguments for this call, matching the tool's `input_schema`. |
| `config` | `Any` | The panel's `PanelConfig` instance, injected by the hub dispatcher. |

**`PanelToolResult`** — returned by the handler:

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | Whether the tool call succeeded. |
| `message` | `str` | A short human-readable summary of the outcome. |
| `data` | `dict` | The structured result payload. Defaults to `{}`. |

**`ToolRegistry`** — collects `PanelTool`s via a `@registry.register(...)` decorator, so each tool's metadata lives directly above the handler it describes instead of in a separate list you have to keep in sync. This is the recommended way to define tools (see below).

### Defining tools

Keep handlers in a dedicated `tools.py` module. Use local imports inside handlers for anything that touches Django models — this keeps the module safe to import at any point in the Django startup sequence.

Instantiate one `ToolRegistry` per `tools.py` module and decorate each handler with `@registry.register(...)`:

```python
# dj_my_panel/tools.py
from dj_control_room_base.core.panel_tool import (
    PanelToolContext,
    PanelToolResult,
    ToolRegistry,
)

registry = ToolRegistry()


@registry.register(
    name="get_item",
    scope="read",
    description="Fetch a single item by key.",
    input_schema={
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "The item key to look up."},
        },
        "required": ["key"],
    },
)
def handle_get_item(ctx: PanelToolContext) -> PanelToolResult:
    from .models import Item  # local import — safe at any startup stage

    key = ctx.inputs["key"]
    try:
        item = Item.objects.get(key=key)
        return PanelToolResult(
            success=True,
            message=f"Found item '{key}'.",
            data={"key": item.key, "value": item.value},
        )
    except Item.DoesNotExist:
        return PanelToolResult(success=False, message=f"Item '{key}' not found.")


@registry.register(
    name="list_items",
    scope="read",
    description="List all items.",
    input_schema={"type": "object", "properties": {}},
)
def handle_list_items(ctx: PanelToolContext) -> PanelToolResult:
    from .models import Item

    items = list(Item.objects.values("key", "value"))
    return PanelToolResult(
        success=True,
        message=f"{len(items)} item(s) found.",
        data={"items": items},
    )
```

The decorator only records metadata as a side effect — it returns the handler unchanged, so `handle_get_item` and `handle_list_items` remain plain, directly callable functions (e.g. in tests, just call `handle_get_item(ctx)`).

### Registering tools on `PanelConfig`

Pass `tools=tool_registry.tools` when instantiating `PanelConfig` in `conf.py`. Tools are not imported at module level — `conf.py` is only loaded when `get_config()` is called at request time.

```python
# dj_my_panel/conf.py
from dj_control_room_base.core import PanelConfig
from dj_my_panel.tools import registry as tool_registry

panel_config = PanelConfig(
    settings_key="DJ_MY_PANEL_SETTINGS",
    defaults={"LOAD_DEFAULT_CSS": True},
    tools=tool_registry.tools,
)
```

The `scope` value (`"read"` above) can be configured by project owners via `SCOPE_PERMISSIONS` in `DJ_MY_PANEL_SETTINGS`, exactly like view scopes.

Panel authors do not need to write any URL configuration for tools as this will be handled by the hub package `dj-control-room` if installed.

#### Building the list manually

`ToolRegistry` is a convenience, not a requirement — `PanelConfig(tools=...)` just needs a `list[PanelTool]`. If you'd rather construct `PanelTool` instances directly (e.g. building the list programmatically from some other source), that still works:

```python
from dj_control_room_base.core.panel_tool import PanelTool
from dj_my_panel.tools import handle_get_item

panel_config = PanelConfig(
    settings_key="DJ_MY_PANEL_SETTINGS",
    tools=[
        PanelTool(
            name="get_item",
            scope="read",
            description="Fetch a single item by key.",
            input_schema={"type": "object", "properties": {"key": {"type": "string"}}},
            handler=handle_get_item,
        ),
    ],
)
```

---

## Full `conf.py` / `views.py` example

```python
# conf.py
from dj_control_room_base.core import PanelConfig

panel_config = PanelConfig(
    settings_key="DJ_MY_PANEL_SETTINGS",
    defaults={
        "LOAD_DEFAULT_CSS": True,
        "EXTRA_CSS": [],
    },
)
```

```python
# views.py
from django.shortcuts import render
from .conf import panel_config


@panel_config.permission_required("main")
def index(request):
    context = panel_config.get_context(request, title="My Panel")
    context["items"] = get_items()  # add your own data
    return render(request, "dj_my_panel/index.html", context)
```

That is the full wiring. One `PanelConfig` declaration in `conf.py` gives all views:

- Consistent permission enforcement
- Automatic CSS injection
- Full Django admin context (breadcrumbs, sidebar, CSRF token, etc.)
- Centralized project-level override via `DJ_MY_PANEL_SETTINGS`

---

## `PanelPlugin` reference

`PanelPlugin` is the base class for all Control Room panel plugins. Subclass it in your panel's `panel.py` and point the `dj_control_room.panels` entry point at your subclass.

| Attribute | Type | Required | Description |
|---|---|---|---|
| `name` | `str` | Yes | Display name shown on the hub dashboard. |
| `description` | `str` | Yes | One-line description shown on the panel card. |
| `icon` | `str` | Yes | Icon key (`database`, `layers`, `link`, `chart`, `radio`, `cog`, `alert`, …). |
| `app_name` | `str` | No | Django app label. Defaults to the normalised PyPI dist name. |
| `package` | `str` | No | PyPI distribution name. Defaults to the dist name from entry-point metadata. |
| `docs_url` | `str` | No | URL to the panel's documentation. |
| `pypi_url` | `str` | No | URL to the panel's PyPI page. |

**Methods:**

| Method | Default | Description |
|---|---|---|
| `get_url_name()` | `"index"` | URL name for the panel's main view. The hub resolves `reverse(f"{app_name}:{get_url_name()}")`. |
| `get_config()` | `None` | Return the panel's `PanelConfig` instance. Override using a local import (see above). |
| `validate()` | — | Assert all required attributes are set. Convenience method for tests; the registry runs its own validation at autodiscovery time. |

---

## `PanelConfig` API reference

### `PanelConfig(settings_key, defaults=None, tools=None)`

Instantiate once in `conf.py`.

| Argument | Type | Description |
|---|---|---|
| `settings_key` | `str` | The Django settings variable name (e.g. `"DJ_MY_PANEL_SETTINGS"`). |
| `defaults` | `dict` | Panel-level defaults merged above built-in defaults but below hub and project settings. |
| `tools` | `list[PanelTool]` | Optional list of `PanelTool` instances exposed to the hub's tool registry. Defaults to `[]`. |

### `panel_config.get_settings(key=None)`

Returns the fully merged settings dict. Pass a key string to retrieve a single value.

### `panel_config.get_context(request, **extra)`

Returns a template context dict with the Django admin context, CSS injection variables, and any extra kwargs. Use this in every view.

### `panel_config.get_css_context()`

Returns only the CSS portion of the context (`dj_cr_load_default_css`, `dj_cr_extra_css`). Useful if you need to merge CSS context separately.

### `panel_config.has_permission(request, scope=None)`

Returns `True` if the request's user may access the panel or a specific scope. Thin wrapper around `_check_permission` for use in view context where a full `request` object is available.

### `panel_config._check_permission(user, scope=None)`

Returns `True` if `user` may access the panel or a specific scope. Operates on a user object directly so it can be called outside of a request context — for example in tool dispatch, management commands, or background tasks.

### `@panel_config.permission_required(scope=None)`

View decorator. Redirects unauthenticated users to the admin login page, raises 403 for authenticated users who fail the permission check.

### `panel_config.apply_override_settings(settings)`

Called by the `dj-control-room` hub to inject cross-panel settings. Panel authors do not call this directly.

---

## `PanelPlaceholderModel` reference

Abstract `managed=False` base model. Subclass it and set `verbose_name` / `verbose_name_plural` in `Meta` to control how the entry appears in the admin sidebar. No migration is generated.

## `BasePanelAdmin` reference

| Attribute | Type | Description |
|---|---|---|
| `redirect_url_name` | `str` | Namespaced URL to redirect the changelist to, e.g. `"my_panel:index"`. |
| `panel_config` | `PanelConfig` | When set, `has_view_permission` and `has_change_permission` delegate to `panel_config.has_permission(request)`. |

All write permissions (`has_add_permission`, `has_delete_permission`) return `False`. The changelist redirects immediately to `redirect_url_name`.
