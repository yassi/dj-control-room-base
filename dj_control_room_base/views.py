from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from dj_control_room_base.conf import panel_config


@staff_member_required
def index(request):
    context = panel_config.get_context(request, title="Dj Control Room Base")
    return render(request, "admin/dj_control_room_base/index.html", context)
