# Importa las utilidades principales del panel de administración de Django.
from django.contrib import admin
# (Opcional) Permite formatear HTML en campos del admin; actualmente sin uso en este archivo.
from django.utils.html import format_html
# Importa todos los modelos definidos en la app para poder registrarlos en el admin.
from app_movil_escolar_api.models import *


# Registra simultáneamente los modelos Administradores, Alumnos y Maestros en el sitio admin.
@admin.register(Administradores, Alumnos, Maestros)
class ProfilesAdmin(admin.ModelAdmin):
    # Define qué columnas se mostrarán en la lista principal del admin para estos modelos.
    list_display = ("id", "user", "creation", "last_update")
    # Permite buscar registros por los campos relacionados del usuario asociado.
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")

    # Método personalizado para exponer el último momento de actualización almacenado en cada objeto.
    def last_update(self, obj):
        # Usa getattr para obtener el atributo 'update' si existe; de lo contrario, devuelve None.
        return getattr(obj, "update", None)
    # Etiqueta legible que se mostrará como encabezado de la columna 'last_update' en el admin.
    last_update.short_description = "update"

