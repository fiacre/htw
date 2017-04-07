# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-24 10:31
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Battle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HashTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('hashtag', models.CharField(max_length=32)),
                ('start_time', models.DateTimeField(blank=True, default=datetime.datetime(2017, 3, 24, 10, 31, 31, 764672, tzinfo=utc))),
                ('end_time', models.DateTimeField(blank=True, default=datetime.datetime(2017, 3, 24, 10, 32, 31, 764701, tzinfo=utc))),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('content', models.CharField(max_length=128)),
                ('num_errors', models.IntegerField(null=True)),
                ('hashtags', models.ManyToManyField(to='wars.HashTag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='battle',
            name='hashtag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wars.HashTag'),
        ),
        migrations.AddField(
            model_name='battle',
            name='user_blue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battle_blue', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='battle',
            name='user_red',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battle_red', to=settings.AUTH_USER_MODEL),
        ),
    ]
