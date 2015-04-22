# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0003_auto_20150422_0259'),
    ]

    operations = [
        migrations.AddField(
            model_name='dia_sprint',
            name='fecha',
            field=models.DateField(null=True),
            preserve_default=True,
        ),
    ]
