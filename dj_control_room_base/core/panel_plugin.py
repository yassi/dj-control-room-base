"""
Base class for DJ Control Room panel plugins.

Panel authors subclass ``PanelPlugin`` and point the
``[project.entry-points."dj_control_room.panels"]`` entry point at their
subclass.  The hub discovers it at startup and uses the declared attributes
to render the dashboard.
"""


class PanelPlugin:
    """
    Base class for a DJ Control Room panel plugin.

    Subclass this in your panel package's ``panel.py`` and register it via
    the ``dj_control_room.panels`` entry point in ``pyproject.toml``.  The
    hub discovers all registered plugins at startup and uses the declared
    attributes to render panel cards, build sidebar entries, and resolve URLs.

    Required attributes:
        name (str): Display name shown in the hub UI.
        description (str): One-line description shown on the panel card.
        icon (str): Icon key (``database``, ``layers``, ``link``, ``chart``,
            ``radio``, ``cog``, ``alert``, …).

    Optional attributes:
        app_name (str): Django app label as declared in ``INSTALLED_APPS`` and
            as the ``app_name`` in your ``urls.py``.  Defaults to the
            normalised PyPI distribution name (hyphens → underscores), which is
            typically the same value.  Only override this when the two differ.
        package (str): PyPI distribution name override.  Defaults to the
            distribution name read from the entry point metadata.
        docs_url (str): URL to the panel's documentation.
        pypi_url (str): URL to the panel's PyPI page.
        features (list[str]): Short one-line descriptions of what this panel
            offers, shown on the install page below the panel description.
            Each item should be a concise capability statement, e.g.
            ``"Browse and search Redis keys"``.  Leave empty (the default)
            to omit the features section entirely.

    Optional methods:
        get_url_name(): URL name for the panel's main view (default ``"index"``).
        get_config(): Returns the panel's :class:`~dj_control_room_base.core.PanelConfig`
            instance, or ``None`` if the panel does not use ``dj-control-room-base``.
            Always use a local import inside this method so that ``conf.py`` is
            not pulled into the module namespace during entry-point discovery::

                def get_config(self):
                    from .conf import panel_config
                    return panel_config

    Note:
        The ``id`` attribute is no longer part of the panel contract.  If
        present on a subclass it is silently ignored — the unique registry key
        is derived from the PyPI distribution name at discovery time.

    Example::

        # mypanel/panel.py
        from dj_control_room_base.core import PanelPlugin

        class MyPanel(PanelPlugin):
            name = "My Panel"
            description = "Does something useful"
            icon = "cog"

            def get_config(self):
                from .conf import panel_config
                return panel_config
    """

    name: str = None
    description: str = None
    icon: str = "default"

    # Stamped by the registry from entry-point metadata if not set explicitly.
    package: str = None
    app_name: str = None

    docs_url: str = None
    pypi_url: str = None
    features: list = []

    def get_config(self):
        """
        Return the panel's :class:`~dj_control_room_base.core.PanelConfig` instance, or ``None``.

        Override in subclasses using a local import so that ``conf.py`` is not
        pulled into the module namespace during entry-point discovery::

            def get_config(self):
                from .conf import panel_config
                return panel_config
        """
        return None

    def get_url_name(self) -> str:
        """
        Return the URL name for this panel's main entry point.

        The hub resolves the panel URL as
        ``reverse(f"{self.app_name}:{self.get_url_name()}")``, so this must
        match a named URL pattern in your ``urls.py``.

        Returns:
            str: The URL name (default: ``"index"``).
        """
        return "index"

    def validate(self) -> None:
        """
        Assert that all required attributes are present and non-empty.

        The registry calls its own validation during autodiscovery, so this
        method is provided as a convenience for panel authors to call in tests
        or during local development.

        Raises:
            ValueError: If a required attribute is missing or empty.
        """
        for attr in ("name", "description", "icon"):
            if not getattr(self, attr, None):
                raise ValueError(
                    f"{self.__class__.__name__} must define a non-empty '{attr}' attribute."
                )
