# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InactiveLockerReservation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_reserved', models.DateTimeField()),
                ('time_unreserved', models.DateTimeField()),
                ('lock_cut', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Locker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('room', models.CharField(verbose_name=b'Rom', max_length=10, editable=False, choices=[(b'CU1-111', b'CU1-111'), (b'CU2-021', b'CU2-021'), (b'EU1-110', b'EU1-110')])),
                ('locker_number', models.IntegerField(verbose_name=b'Skapnummer', editable=False)),
                ('time_reserved', models.DateTimeField(null=True, blank=True)),
                ('owner', models.ForeignKey(verbose_name=b'Eier', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='locker',
            unique_together=set([('room', 'locker_number')]),
        ),
        migrations.AddField(
            model_name='inactivelockerreservation',
            name='locker',
            field=models.ForeignKey(to='locker.Locker'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inactivelockerreservation',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
