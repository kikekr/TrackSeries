# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Capitulo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('temporada', models.IntegerField()),
                ('numero', models.IntegerField()),
                ('titulo', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Serie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.CharField(max_length=500)),
                ('imagen', models.CharField(max_length=100)),
                ('genero', models.CharField(max_length=100)),
                ('fechaEmision', models.CharField(max_length=100)),
                ('estado', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='capitulo',
            name='serie',
            field=models.ForeignKey(to='series.Serie'),
        ),
    ]
