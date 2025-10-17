# Importa utilidades de borrado para claves foraneas.
import django.db.models.deletion
# Referencia la configuracion global para acceder al modelo de usuario.
from django.conf import settings
# Incluye las herramientas para definir migraciones y tipos de campos.
from django.db import migrations, models


class Migration(migrations.Migration):
    # Define que esta migracion depende de la anterior y del modelo de usuario configurable.
    dependencies = [
        ('app_movil_escolar_api', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    # Lista de operaciones que modifican la base de datos.
    operations = [
        migrations.CreateModel(
            # Nuevo modelo Administradores en la base de datos.
            name='Administradores',
            # Campos que componen la tabla.
            fields=[
                # Clave primaria autoincremental tipo BigAutoField.
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                # Clave interna opcional para identificar al administrador.
                ('clave_admin', models.CharField(blank=True, max_length=255, null=True)),
                # Numero telefonico del administrador.
                ('telefono', models.CharField(blank=True, max_length=255, null=True)),
                # RFC opcional del administrador.
                ('rfc', models.CharField(blank=True, max_length=255, null=True)),
                # Edad del administrador; puede omitirse.
                ('edad', models.IntegerField(blank=True, null=True)),
                # Ocupacion o puesto del administrador.
                ('ocupacion', models.CharField(blank=True, max_length=255, null=True)),
                # Fecha de creacion automatica del registro.
                ('creation', models.DateTimeField(auto_now_add=True, null=True)),
                # Fecha de ultima actualizacion manual.
                ('update', models.DateTimeField(blank=True, null=True)),
                # Relacion con el usuario dueno del registro.
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            # Elimina la tabla Profiles creada en la migracion anterior.
            name='Profiles',
        ),
    ]
