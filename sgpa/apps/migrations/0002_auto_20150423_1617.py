# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userstory',
            old_name='tiempoEstimado',
            new_name='tiempo_Estimado',
        ),
        migrations.RenameField(
            model_name='userstory',
            old_name='tiempoReal',
            new_name='tiempo_Real',
        ),
        migrations.RenameField(
            model_name='userstory',
            old_name='usuarioAsignado',
            new_name='usuario_Asignado',
        ),
        migrations.RemoveField(
            model_name='userstory',
            name='valorNegocio',
        ),
        migrations.RemoveField(
            model_name='userstory',
            name='valorTecnico',
        ),
        migrations.AddField(
            model_name='userstory',
            name='valor_Negocio',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userstory',
            name='valor_Tecnico',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userstory',
            name='codigo',
            field=models.CharField(max_length=30),
            preserve_default=True,
        ),
    ]
