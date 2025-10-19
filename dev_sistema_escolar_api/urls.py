from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from dev_sistema_escolar_api.views.admin import AdminView
from dev_sistema_escolar_api.views.maestro import MaestroView
from dev_sistema_escolar_api.views.estudiante import EstudianteView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/version/", VersionView.as_view(), name="api-version"),
    path("api/admins/", AdminView.as_view(), name="api-admin-create"),
    path("api/estudiantes/", EstudianteView.as_view(), name="api-estudiante-create"),
    path("api/maestros/", MaestroView.as_view(), name="api-maestro-create"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
