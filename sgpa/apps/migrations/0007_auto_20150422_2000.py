# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0006_dia_sprint_proyecto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dia_sprint',
            name='proyecto',
        ),
        migrations.AlterField(
            model_name='dia_sprint',
            name='sprint',
            field=models.ForeignKey(blank=True, to='apps.Sprint', null=True),
            preserve_default=True,
        ),
    ]
