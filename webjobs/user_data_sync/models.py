import os
from peewee import MySQLDatabase, Model, BooleanField, CharField, TextField, DateTimeField, ForeignKeyField

mysql_host = os.environ['MySQLHost']
mysql_port = int('3306')
mysql_name = 'edu'
mysql_user = os.environ['MySQLUser']
mysql_password = os.environ['MySQLPassword']

db = MySQLDatabase(mysql_name, user=mysql_user, password=mysql_password, host=mysql_host, port=mysql_port)

class BaseModel(Model):
    class Meta:
        database = db

class Organization(BaseModel):
    # id = AutoField(primary_key=True)
    name = CharField()
    tenantId = CharField()
    isAdminConsented = BooleanField()
    class Meta:
        db_table = "organizations"

class Profile(BaseModel):
    # user = OneToOneField(User, on_delete=None)
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

# db.connect()

# organizations = Organization.select() \
#     .where(Organization.isAdminConsented)

# for org in organizations:
#     print(org.name)


# profiles = Profile.select()

# for profile in profiles:
#     print(profile.o365Email)

# db.close()