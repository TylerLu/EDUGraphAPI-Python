from django.db import models

from django.contrib.auth.models import User

class LocalUser(models.Model):
    user = models.OneToOneField(User)
    o365UserId = models.CharField(null=True, max_length=255)
    o365Email = models.CharField(null=True, max_length=255)
    favoriteColor = models.CharField(null=True, max_length=255)
    class Meta:
        db_table = 'users'

class UserRoles(models.Model):
    name = models.CharField(null=True, max_length=255)
    o365UserId = models.CharField(null=True, max_length=255)
    class Meta:
        db_table = 'user_roles'

class TokenCache(models.Model):
    o365UserId = models.CharField(null=True, max_length=255)
    refreshToken = models.TextField(null=True)
    accessToken = models.TextField(null=True)
    expiresOn = models.CharField(null=True, max_length=255)
    resource = models.CharField(null=True, max_length=255)
    class Meta:
        db_table = 'token_cache'

class ClassroomSeatingArrangements(models.Model):
    id = models.AutoField(primary_key=True)
    position = models.IntegerField()
    userId = models.CharField(null=True, max_length=255)
    classId = models.CharField(null=True, max_length=255)
    class Meta:
        db_table = 'classroom_seating_arranements'
