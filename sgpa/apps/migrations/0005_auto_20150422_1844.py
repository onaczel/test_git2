# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0004_dia_sprint_fecha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dia_sprint',
            name='sprint',
            field=models.IntegerField(),
            preserve_default=True,
        ),
    ]
