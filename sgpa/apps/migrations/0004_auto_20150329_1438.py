# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0003_auto_20150329_1436'),
    ]

    operations = [
        migrations.RenameField(
            model_name='actividades',
            old_name='flujo_id',
            new_name='flujo',
        ),
        migrations.RenameField(
            model_name='actividades_estados',
            old_name='actividad_id',
            new_name='actividad',
        ),
        migrations.RenameField(
            model_name='actividades_estados',
            old_name='estados_id',
            new_name='estados',
        ),
    ]
