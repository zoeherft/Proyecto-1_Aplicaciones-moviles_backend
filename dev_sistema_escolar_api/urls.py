from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from dev_sistema_escolar_api.views.admin import AdminView, AdminsAll
from dev_sistema_escolar_api.views.maestro import MaestroView, MaestrosAll
from dev_sistema_escolar_api.views.alumno import AlumnoView, AlumnosAll

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/version/", VersionView.as_view(), name="api-version"),
    path("api/admins/", AdminView.as_view(), name="api-admin-create"),
    path("api/admins-all/", AdminsAll.as_view(), name="api-admins-all"),
    path("api/alumnos/", AlumnoView.as_view(), name="api-Alumno-create"),
    path("api/alumnos-all/", AlumnosAll.as_view(), name="api-alumnos-all"),
    path("api/maestros/", MaestroView.as_view(), name="api-maestro-create"),
    path("api/maestros-all/", MaestrosAll.as_view(), name="api-maestros-all"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
