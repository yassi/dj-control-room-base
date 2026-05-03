from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse


class BasePanelAdmin(admin.ModelAdmin):
    """
    Base admin class for Control Room panel placeholder models.

    Redirects the changelist to the panel's main view and restricts all write
    permissions so the admin sidebar entry is read-only.

    Required class attribute:
        redirect_url_name (str): Namespaced URL name to redirect to,
            e.g. ``"my_panel:index"``.

    Optional class attribute:
        panel_config (PanelConfig): When set, ``has_view_permission`` and
            ``has_change_permission`` delegate to
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
