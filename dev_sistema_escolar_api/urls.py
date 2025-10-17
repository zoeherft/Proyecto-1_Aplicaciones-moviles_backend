from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from .views.users import AdminView, EstudianteView, MaestroView, Userme

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/version/", VersionView.as_view(), name="api-version"),
    path("api/user/me/", Userme.as_view(), name="api-user-me"),
    path("api/admins/", AdminView.as_view(), name="api-admin-create"),
    path("api/estudiantes/", EstudianteView.as_view(), name="api-estudiante-create"),
    path("api/maestros/", MaestroView.as_view(), name="api-maestro-create"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
