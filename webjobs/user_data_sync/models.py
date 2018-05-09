import os
import constants
from peewee import MySQLDatabase, Model, PrimaryKeyField, BooleanField, CharField, TextField, DateTimeField, ForeignKeyField

database  = MySQLDatabase(constants.mysql_name, 
    user=constants.mysql_user, 
    password=constants.mysql_password, 
    host=constants.mysql_host, 
    port=constants.mysql_port)

class BaseModel(Model):
    class Meta:
        database = database 

class User(BaseModel):
    id = PrimaryKeyField(null=False)
    username = CharField()
    class Meta:
        db_table = "auth_user"

class UserRole(BaseModel):
    id = PrimaryKeyField(null=False)
    name = CharField()
    o365UserId = CharField()
    class Meta:
        db_table = "user_roles"

class TokenCache(BaseModel):
    id = PrimaryKeyField(null=False)
    o365UserId = CharField()
    class Meta:
        db_table = "token_cache"

class Organization(BaseModel):
    id = PrimaryKeyField(null=False)
    name = CharField()
    tenantId = CharField()
    isAdminConsented = BooleanField()

    @staticmethod
    def get_consented():
        return Organization.select().where(Organization.isAdminConsented)

    class Meta:
        db_table = "organizations"

class Profile(BaseModel):
    user = ForeignKeyField(User, primary_key=True, on_delete='CASCADE')
    o365UserId = CharField()
    o365Email = CharField()
    jobTitle = CharField()
    department = CharField()
    mobilePhone = CharField()
    organization = ForeignKeyField(Organization)
    class Meta:
        db_table = "profiles"

class DataSyncRecord(BaseModel):
    id = PrimaryKeyField(null=False)
    tenantId = CharField()
    query = TextField()
    deltaLink = TextField()
    updated = DateTimeField(null=True)
    class Meta:
        db_table = 'data_sync_records'