from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from accounts.spa import spa_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    assets_dir = settings.FRONTEND_DIR / "assets"
    if assets_dir.exists():
        urlpatterns += [
            path("assets/<path:path>", serve, {"document_root": assets_dir}),
        ]

urlpatterns += [
    re_path(r"^(?!api/|admin/|media/|assets/).*$", spa_view, name="spa"),
]
