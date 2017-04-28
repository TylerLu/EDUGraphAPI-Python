# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-27 09:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassroomSeatingArrangements',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('position', models.IntegerField()),
                ('userId', models.CharField(max_length=255, null=True)),
                ('classId', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'classroom_seating_arranements',
            },
        ),
        migrations.CreateModel(
            name='LocalUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('o365UserId', models.CharField(max_length=255, null=True)),
                ('o365Email', models.CharField(max_length=255, null=True)),
                ('favoriteColor', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='Organizations',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, null=True)),
                ('tenantId', models.CharField(max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('isAdminConsented', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'organizations',
            },
        ),
        migrations.CreateModel(
            name='TokenCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('o365UserId', models.CharField(max_length=255, null=True)),
                ('refreshToken', models.TextField(null=True)),
                ('accessToken', models.TextField(null=True)),
                ('expiresOn', models.CharField(max_length=255, null=True)),
                ('resource', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'token_cache',
            },
        ),
        migrations.CreateModel(
            name='UserRoles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('o365UserId', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'user_roles',
            },
        ),
        migrations.AddField(
            model_name='localuser',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.Organizations'),
        ),
        migrations.AddField(
            model_name='localuser',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
