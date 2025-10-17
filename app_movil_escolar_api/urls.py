from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from app_movil_escolar_api.views import bootstrap
from app_movil_escolar_api.views import users, alumnos, maestros
from app_movil_escolar_api.views import auth
# from sistema_escolar_api.views import alumnos
# from sistema_escolar_api.views import maestros

urlpatterns = [
    #Create Admin
        path('admin/', users.AdminView.as_view()),
    #Admin Data
        path('lista-admins/', users.AdminAll.as_view()),
    #Create Alumno
        path('alumnos/', alumnos.AlumnosView.as_view()),
        path('alumnos/<int:pk>/', alumnos.AlumnoDetailView.as_view()),
    #Create Maestro
        path('maestros/', maestros.MaestrosView.as_view()),
        path('maestros/<int:pk>/', maestros.MaestroDetailView.as_view()),
    #Edit Admin
        #path('admins-edit/', users.AdminsViewEdit.as_view())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
