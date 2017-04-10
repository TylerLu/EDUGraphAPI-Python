from __future__ import unicode_literals

from django.db import models

# Create your models here.
class AdUsers(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=True)
    token = models.TextField(null=True)
    token_type = models.TextField(null=True)
    o365_email = models.CharField(null=True, max_length=255)
    class Meta:
        db_table = 'ad_users'

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    firstName = models.CharField(null=True, max_length=255)
    lastName = models.CharField(null=True, max_length=255)
    password = models.CharField(null=True, max_length=255)
    email = models.CharField(null=True, max_length=255)
    class Meta:
        db_table = 'users'
