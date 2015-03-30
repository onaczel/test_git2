# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0004_auto_20150329_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='actividades',
            name='estado',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
