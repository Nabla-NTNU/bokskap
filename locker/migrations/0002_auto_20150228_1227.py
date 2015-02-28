# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('locker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locker',
            name='locker_number',
            field=models.IntegerField(verbose_name='Skapnummer', editable=False),
        ),
        migrations.AlterField(
            model_name='locker',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL, verbose_name='Eier'),
        ),
        migrations.AlterField(
            model_name='locker',
            name='room',
            field=models.CharField(max_length=10, choices=[('CU1-111', 'CU1-111'), ('CU2-021', 'CU2-021'), ('EU1-110', 'EU1-110')], verbose_name='Rom', editable=False),
        ),
    ]
