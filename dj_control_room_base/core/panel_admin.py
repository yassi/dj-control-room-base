from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse


class BasePanelAdmin(admin.ModelAdmin):
    """
    Base admin class for Control Room panel placeholder models.

    Redirects the changelist to the panel's main view and restricts all write
    permissions so the admin sidebar entry is read-only.

    Overrides ``has_module_permission`` and ``get_model_perms`` so that staff
    users (or users satisfying ``panel_config``'s permission rules) see the
    sidebar entry without needing a ContentType-backed ``Permission`` row in the
    database.

    Required class attribute:
        redirect_url_name (str): Namespaced URL name to redirect to,
            e.g. ``"my_panel:index"``.

    Optional class attribute:
        panel_config (PanelConfig): When set, all permission checks delegate to
            ``panel_config.has_permission(request)`` rather than the default
            ``is_staff`` check.  Set this to the panel's ``conf.panel_config``
            instance so that the sidebar entry respects the panel's configured
            permission rules.

    Example::

        from dj_control_room_base.core import BasePanelAdmin
        from .conf import panel_config
        from .models import MyPanelPlaceholder

        @admin.register(MyPanelPlaceholder)
        class MyPanelAdmin(BasePanelAdmin):
            redirect_url_name = "my_panel:index"
            panel_config = panel_config
    """

    redirect_url_name: str = None
    panel_config = None

    def _check_permission(self, request) -> bool:
        if self.panel_config is not None:
            return self.panel_config.has_permission(request)
        return request.user.is_staff

    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect(reverse(self.redirect_url_name))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return self._check_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return self._check_permission(request)

    def has_module_permission(self, request):
        """
        Controls whether the app section appears in the admin sidebar at all.

        Django's ``_build_app_dict`` calls this before ``get_model_perms``, so
        it must be overridden to bypass the default ``user.has_module_perms``
        DB check (which requires a ContentType-backed Permission row).
        """
        return self._check_permission(request)

    def get_model_perms(self, request):
        """
        Controls whether this model entry appears within its app section.

        Returns the permission dict consulted by ``_build_app_dict`` after
        ``has_module_permission`` passes.  We drive visibility from
        ``_check_permission`` rather than DB permissions.
        """
        has_perm = self._check_permission(request)
        return {
            "add": False,
            "change": has_perm,
            "delete": False,
            "view": has_perm,
        }
