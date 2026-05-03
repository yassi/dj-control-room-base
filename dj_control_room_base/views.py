from django.shortcuts import render

from dj_control_room_base.conf import panel_config


@panel_config.permission_required()
def index(request):
    context = panel_config.get_context(request, title="DCR Design System")
    return render(request, "admin/dj_control_room_base/index.html", context)


@panel_config.permission_required("examples")
def examples(request):
    context = panel_config.get_context(request, title="Reference Examples")
    return render(request, "admin/dj_control_room_base/examples.html", context)
