

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_movil_escolar_api', '0003_alumnos_maestros'),
    ]

    operations = [
        migrations.AddField(
            model_name='alumnos',
            name='curp',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='alumnos',
            name='edad',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='alumnos',
            name='fecha_nacimiento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='alumnos',
            name='matricula',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='alumnos',
            name='ocupacion',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='alumnos',
            name='rfc',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='maestros',
            name='area_investigacion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='maestros',
            name='cubiculo',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='maestros',
            name='fecha_nacimiento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='maestros',
            name='id_trabajador',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='maestros',
            name='materias_json',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='maestros',
            name='rfc',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
