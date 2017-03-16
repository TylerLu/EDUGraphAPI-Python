# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-06 09:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdUsers',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(null=True)),
                ('token', models.TextField(null=True)),
                ('token_type', models.TextField(null=True)),
                ('o365_email', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'ad_users',
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('firstName', models.CharField(max_length=255, null=True)),
                ('lastName', models.CharField(max_length=255, null=True)),
                ('password', models.CharField(max_length=255, null=True)),
                ('email', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'users',
            },
        ),
    ]
