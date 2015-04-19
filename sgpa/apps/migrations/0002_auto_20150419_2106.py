# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstory',
            name='estado',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userstory',
            name='flujo',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userstory',
            name='prioridad',
            field=models.ForeignKey(to='apps.Prioridad', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userstory',
            name='proyecto',
            field=models.ForeignKey(to='apps.Proyectos', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userstory',
            name='sprint',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userstory',
            name='tiempoReal',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userstory',
            name='usuarioAsignado',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
