from django.contrib.auth.models import User
from django.db import models
from rest_framework.authentication import TokenAuthentication

class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"


class Administradores(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    clave_admin = models.CharField(max_length=255,null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    rfc = models.CharField(max_length=255,null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    ocupacion = models.CharField(max_length=255,null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        full_name = self.user.get_full_name() or self.user.username
        return f"Perfil del admin {full_name}"


class Estudiantes(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    matricula = models.CharField(max_length=50, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    curp = models.CharField(max_length=18, null=True, blank=True)
    rfc = models.CharField(max_length=13, null=True, blank=True)
    edad = models.PositiveIntegerField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    ocupacion = models.CharField(max_length=255, null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Perfil del estudiante {self.user.get_full_name() or self.user.username}"


class Maestros(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    id_trabajador = models.CharField(max_length=50, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    rfc = models.CharField(max_length=13, null=True, blank=True)
    cubiculo = models.CharField(max_length=255, null=True, blank=True)
    area_investigacion = models.CharField(max_length=255, null=True, blank=True)
    materias_json = models.JSONField(default=list, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Perfil del maestro {self.user.get_full_name() or self.user.username}"
