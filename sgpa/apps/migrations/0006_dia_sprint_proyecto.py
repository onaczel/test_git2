# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0005_auto_20150422_1844'),
    ]

    operations = [
        migrations.AddField(
            model_name='dia_sprint',
            name='proyecto',
            field=models.ForeignKey(default=None, to='apps.Proyectos'),
            preserve_default=False,
        ),
    ]
