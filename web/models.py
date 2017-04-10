from __future__ import unicode_literals

from django.db import models

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    firstName = models.CharField(null=True, max_length=255)
    lastName = models.CharField(null=True, max_length=255)
    password = models.CharField(null=True, max_length=255)
    email = models.CharField(null=True, unique=True, max_length=255)
    o365UserId = models.CharField(null=True, max_length=255)
    o365Email = models.CharField(null=True, max_length=255)
    favoriteColor = models.CharField(null=True, max_length=255)
    class Meta:
        db_table = 'users'

class ClassroomSeatingArrangements(models.Model):
    id = models.AutoField(primary_key=True)
    position = models.IntegerField()
    userId = models.CharField(null=True, max_length=255)
    classId = models.CharField(null=True, max_length=255)
    class Meta:
        db_table = 'classroomseating'
