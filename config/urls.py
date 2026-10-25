from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("dashboard/", include("dashboard.urls")),
    path("", include("orders.urls")),
    path("", include("store.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
