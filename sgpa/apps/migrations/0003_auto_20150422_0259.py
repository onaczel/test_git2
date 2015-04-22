# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_auto_20150419_2106'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dia_Sprint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tiempo_estimado', models.IntegerField()),
                ('tiempo_real', models.IntegerField()),
                ('dia', models.IntegerField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nro_sprint', models.IntegerField()),
                ('proyecto', models.ForeignKey(blank=True, to='apps.Proyectos', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='dia_sprint',
            name='sprint',
            field=models.ForeignKey(blank=True, to='apps.Sprint', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='permisos',
            name='sistema',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='roles',
            name='sistema',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
