import os
import constants
from peewee import MySQLDatabase, Model, BooleanField, CharField, TextField, DateTimeField, ForeignKeyField

database  = MySQLDatabase(constants.mysql_name, 
    user=constants.mysql_user, 
    password=constants.mysql_password, 
    host=constants.mysql_host, 
    port=constants.mysql_port)

class BaseModel(Model):
    class Meta:
        database = database 

class Organization(BaseModel):
    name = CharField()
    tenantId = CharField()
    isAdminConsented = BooleanField()

    @staticmethod
    def get_consented():
        return Organization.select().where(Organization.isAdminConsented)

    class Meta:
        db_table = "organizations"

class Profile(BaseModel):
    o365UserId = CharField()
    o365Email = CharField()
    jobTitle = CharField()
    department = CharField()
    mobilePhone = CharField()
    organization = ForeignKeyField(Organization, related_name="organizations")
    class Meta:
        db_table = "profiles"

class DataSyncRecord(BaseModel):
    tenantId = CharField()
    query = TextField()
    deltaLink = TextField()
    updated = DateTimeField(null=True)
    class Meta:
        db_table = 'data_sync_records'