# Importa las utilidades de migraciones y los tipos de campos necesarios.
from django.db import migrations, models


class Migration(migrations.Migration):
    # Esta migracion depende de la creacion de Alumnos y Maestros.
    dependencies = [
        ('app_movil_escolar_api', '0003_alumnos_maestros'),
    ]

    # Operaciones para anadir campos extra a los modelos existentes.
    operations = [
        migrations.AddField(
            # Campo CURP opcional para alumnos.
            model_name='alumnos',
            name='curp',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            # Guarda la edad del alumno si esta disponible.
            model_name='alumnos',
            name='edad',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            # Fecha de nacimiento registrada para el alumno.
            model_name='alumnos',
            name='fecha_nacimiento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            # Matricula institucional del alumno.
            model_name='alumnos',
            name='matricula',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            # Ocupacion o rol laboral del alumno (si aplica).
            model_name='alumnos',
            name='ocupacion',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            # RFC opcional del alumno.
            model_name='alumnos',
            name='rfc',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            # Area o linea de investigacion asociada al maestro.
            model_name='maestros',
            name='area_investigacion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            # Numero o referencia del cubiculo del maestro.
            model_name='maestros',
            name='cubiculo',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            # Fecha de nacimiento del maestro.
            model_name='maestros',
            name='fecha_nacimiento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            # Identificador interno para el maestro dentro de la institucion.
            model_name='maestros',
            name='id_trabajador',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            # Lista de materias que imparte el maestro serializada como JSON.
            model_name='maestros',
            name='materias_json',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            # RFC del maestro en caso de estar registrado.
            model_name='maestros',
            name='rfc',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
