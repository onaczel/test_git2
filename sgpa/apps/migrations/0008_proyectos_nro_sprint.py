# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0007_auto_20150422_2000'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyectos',
            name='nro_sprint',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
