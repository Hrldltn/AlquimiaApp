# Generated by Django 4.2.7 on 2023-12-08 14:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('AlquimiaApp', '0003_alter_inventario_fecha_alter_venta_fecha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendario',
            name='nombre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Encargado'),
        ),
    ]
