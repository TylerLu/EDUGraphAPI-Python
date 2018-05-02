'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class Organization(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=255)
    tenantId = models.CharField(null=True, max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    isAdminConsented = models.BooleanField(default=False)
    class Meta:
        db_table = 'organizations'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=None)
    o365UserId = models.CharField(null=True, max_length=255)
    o365Email = models.CharField(null=True, max_length=255)
    favoriteColor = models.CharField(null=True, max_length=255)
    jobTitle = models.CharField(null=True, max_length=255)
    department = models.CharField(null=True, max_length=255)
    mobilePhone = models.CharField(null=True, max_length=255)
    organization = models.ForeignKey(Organization, models.SET_NULL, null=True)
    class Meta:
        db_table = 'profiles'

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

class UserRole(models.Model):
    name = models.CharField(null=True, max_length=255)
    o365UserId = models.CharField(null=True, max_length=255)
    class Meta:
        db_table = 'user_roles'

class TokenCache(models.Model):
    o365UserId = models.CharField(null=True, max_length=255)
    refreshToken = models.TextField(null=True)
    accessToken = models.TextField(null=True)
    expiresOn = models.DateTimeField(null=True)
    resource = models.CharField(null=True, max_length=255)
    class Meta:
        db_table = 'token_cache'

class ClassroomSeatingArrangement(models.Model):
    id = models.AutoField(primary_key=True)
    position = models.IntegerField()
    userId = models.CharField(null=True, max_length=255)
    classId = models.CharField(null=True, max_length=255)
    class Meta:
        db_table = 'classroom_seating_arranements'

class DataSyncRecord(models.Model):
    id = models.AutoField(primary_key=True)
    tenantId = models.CharField(null=True, max_length=255)
    query = models.TextField(null=True)
    deltaLink = models.TextField(null=True)
    updated = models.DateTimeField()
    class Meta:
        db_table = 'data_sync_record'