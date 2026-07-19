# Installation

## Requirements

- Python 3.9+
- Django 4.2+

---

## 1. Install the package

```bash
pip install dj-control-room-base
```

To also install the [Control Room hub](https://github.com/django-control-room/dj-control-room) (centralized dashboard for all panels):

```bash
pip install dj-control-room-base dj-control-room
```

---

## 2. Add to `INSTALLED_APPS`

=== "Standalone (library or panel only)"

    ```python
    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "dj_control_room_base",
    ]
    ```

=== "With Control Room hub"

    ```python
    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "dj_control_room",        # hub dashboard
        "dj_control_room_base",   # this panel / core library
    ]
    ```

---

## 3. Include URLs

=== "Standalone"

    ```python
    # urls.py
    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        path("admin/dj-control-room-base/", include("dj_control_room_base.urls")),
        path("admin/", admin.site.urls),
    ]
    ```

=== "With Control Room hub"

    ```python
    # urls.py
    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        path("admin/dj-control-room-base/", include("dj_control_room_base.urls")),
        path("admin/dj-control-room/", include("dj_control_room.urls")),
        path("admin/", admin.site.urls),
    ]
    ```

The URL prefix (`admin/dj-control-room-base/`) can be changed to whatever fits your project. The admin sidebar entry will still redirect users to the correct view via the named URL `dj_control_room_base:index`.

---

## 4. Run migrations

```bash
python manage.py migrate
```

!!! note
    `dj_control_room_base` itself has no database tables. The `migrate` command is only needed for Django's built-in apps (auth, sessions, etc.). The admin sidebar entry uses a `managed = False` placeholder model - no migration is generated for it.

---

## 5. Create a superuser (if needed)

```bash
python manage.py createsuperuser
```

---

## 6. Start the server and verify

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/admin/` and sign in. You should see a **DJ CONTROL ROOM BASE** section in the sidebar. Clicking the entry redirects you to the panel at `/admin/dj-control-room-base/`.

If you installed `dj-control-room`, open `http://127.0.0.1:8000/admin/dj-control-room/` to see the hub dashboard with the panel listed.

---

## Using as a library only

If you only want to use the shared primitives (`PanelPlugin`, `PanelConfig`, `PanelPlaceholderModel`, `BasePanelAdmin`) in your own panel without mounting this package's views or sidebar entry, you still need to add it to `INSTALLED_APPS` so Django can discover the static files and templates. You do not need to include the URLs.

```python
INSTALLED_APPS = [
    ...
    "dj_control_room_base",  # needed for staticfiles and template discovery
]
# No URL include required when using as a library only
```

See [Building Panels](building-panels.md) for a full guide on using the library primitives in your own panel.
