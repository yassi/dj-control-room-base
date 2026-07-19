# Development

Setting up the project for local development and contributing.

---

## Prerequisites

- Python 3.9+
- Git
- Docker and Docker Compose (recommended for running services)

---

## 1. Clone the repository

```bash
git clone https://github.com/django-control-room/dj-control-room-base.git
cd dj-control-room-base
```

---

## 2. Set up the development environment

=== "Docker (recommended)"

    Docker Compose provides a **dev** container with the full environment pre-configured, plus a **Postgres** service for database-backed test runs.

    ```bash
    make docker_up      # start all services
    make docker_shell   # open a shell in the dev container
    ```

    The dev container mounts the repo at `/app` with the working directory set to `/app/example_project`. From inside the shell:

    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver 0.0.0.0:8000
    ```

    The server is available at `http://localhost:8000/admin/` from your host machine.

    To stop all services and clean up volumes:

    ```bash
    make docker_down
    ```

=== "Local virtualenv"

    ```bash
    python -m venv .venv
    source .venv/bin/activate   # Windows: .venv\Scripts\activate
    make install                # installs requirements.txt + package in editable mode
    ```

    Then set up the example project:

    ```bash
    cd example_project
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver
    ```

---

## Running tests

The test suite lives in `tests/` and uses `example_project` as the Django settings module. SQLite is used by default.

=== "Local"

    ```bash
    make test_local
    # equivalent to:
    python -m pytest tests/ -v
    ```

=== "Docker"

    ```bash
    make test_docker
    ```

    This starts the Compose services, waits for them to be ready, then runs the full test suite inside the dev container.

=== "Postgres"

    To run tests against Postgres instead of SQLite, set `TEST_DB_BACKEND=postgresql` and ensure the Postgres service is running:

    ```bash
    make docker_up
    docker compose exec dev bash -c "TEST_DB_BACKEND=postgresql python -m pytest tests/ -v"
    ```

---

## Coverage

```bash
make test_coverage
```

Generates an XML report (`coverage.xml`), an HTML report (`htmlcov/`), and a terminal summary. Open `htmlcov/index.html` in a browser for the full line-by-line report.

```bash
make coverage_html   # runs test_coverage and prints the htmlcov path
```

---

## Project structure

```
dj-control-room-base/
├── dj_control_room_base/
│   ├── core/
│   │   ├── panel_config.py    # PanelConfig, PANEL_BUILTIN_DEFAULTS
│   │   ├── admin.py           # BasePanelAdmin
│   │   └── models.py          # PanelPlaceholderModel
│   ├── templates/             # Panel HTML templates
│   ├── static/                # design-system.css and other assets
│   ├── conf.py                # PanelConfig instance for this panel
│   ├── panel.py               # Control Room entry-point class
│   ├── views.py               # index and examples views
│   ├── urls.py                # URL patterns
│   ├── admin.py               # BasePanelPlaceholderAdmin registration
│   └── models.py              # BasePanelPlaceholder model
├── example_project/           # Runnable Django project used in tests
│   └── example_project/
│       ├── management/commands/
│       │   └── render_design_system.py  # generates docs/design-system.html
│       ├── settings.py        # Test/dev settings (SQLite + Postgres toggle)
│       └── urls.py
├── tests/
│   ├── conftest.py            # Pytest/Django setup
│   ├── base.py                # Shared test base class
│   ├── test_admin.py          # Admin integration tests
│   ├── test_core_admin.py     # BasePanelAdmin unit tests
│   └── test_panel_config.py   # PanelConfig unit tests
├── docs/                      # This documentation site
├── images/                    # Screenshots used in README and docs
├── mkdocs.yml                 # Documentation site config
├── pyproject.toml
├── requirements.txt           # Dev dependencies
└── Makefile
```

---

## Design system reference page

`docs/design-system.html` is a committed, self-contained HTML file that serves as the static design system reference in the docs site. It is not regenerated automatically on every build - it is a maintained static artifact that you update intentionally when the design system templates change.

To regenerate it after modifying `sg_partials/*.html` templates or `design-system.css`:

```bash
make render_design_system
# equivalent to:
python example_project/manage.py render_design_system --output docs/design-system.html
```

Then review the diff and commit the updated file alongside your template changes.

The command renders all seven `sg_partials/*.html` templates via Django's template engine and inlines `design-system.css`, `styles.css`, and the syntax-highlighting assets into a single self-contained file. No database or authentication is required.

---

## Makefile reference

| Command | Description |
|---|---|
| `make install` | Install `requirements.txt` and the package in editable mode. |
| `make test_local` | Run the full test suite locally with pytest. |
| `make test_docker` | Run the test suite inside the Docker dev container. |
| `make test_coverage` | Run tests with coverage (XML + HTML + terminal). |
| `make coverage_html` | Same as above, prints the HTML report path. |
| `make docker_up` | Start all Docker Compose services. |
| `make docker_down` | Stop all services and remove volumes. |
| `make docker_shell` | Open an interactive shell in the dev container. |
| `make build` | Build sdist and wheel into `dist/`. |
| `make publish` | Upload `dist/` to PyPI via twine. |
| `make docs` | Render design system page, then build the MkDocs site into `site/`. |
| `make docs_serve` | Serve the docs locally at `http://127.0.0.1:8000`. |
| `make docs_push` | Build and deploy docs to GitHub Pages. |
| `make clean` | Remove build artifacts (`build/`, `dist/`, `*.egg-info`). |

---

## CI

Tests run on GitHub Actions across the full matrix of supported Python and Django versions. See `.github/workflows/test.yml` for the exact matrix.

Coverage is uploaded to [Codecov](https://codecov.io/gh/django-control-room/dj-control-room-base) on every push.

---

## Contributing

1. Fork the repository and create a feature branch.
2. Make your changes and add tests for any new behavior.
3. Run `make test_local` to confirm everything passes.
4. Open a pull request against `main`.

Please follow PEP 8, use type hints for public method signatures, and keep functions focused. No em dashes in documentation or code comments.
