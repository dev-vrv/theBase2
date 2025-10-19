from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import path


def index(_request):
    return HttpResponse("ok", content_type="text/plain")


def health(_):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", index, name="index"),
    path("admin/", admin.site.urls),
]

urlpatterns += [path("health/", health)]
