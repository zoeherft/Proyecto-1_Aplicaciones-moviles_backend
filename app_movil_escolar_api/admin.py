from django.contrib import admin
from django.utils.html import format_html
from app_movil_escolar_api.models import *


@admin.register(Administradores, Alumnos, Maestros)
class ProfilesAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "creation", "last_update")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")

    def last_update(self, obj):
        return getattr(obj, "update", None)
    last_update.short_description = "update"

