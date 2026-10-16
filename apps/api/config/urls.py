from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def health(request):
    return JsonResponse({"status": "ok", "service": "infinite-mushrooms-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health),
]
