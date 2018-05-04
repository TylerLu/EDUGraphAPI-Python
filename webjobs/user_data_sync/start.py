import os
import adal
import datetime

from OpenSSL import crypto
from cryptography.hazmat.primitives import serialization

from rest_api_service import RestApiService
import models 

client_id = os.environ['ClientId']
client_cert_path = os.environ['ClientCertificatePath']
client_cert_password = os.environ['ClientCertificatePassword']

aad_instance = 'https://login.microsoftonline.com/'
ms_graph_resource = 'https://graph.microsoft.com'

users_query = "/users/delta?$select=jobTitle,department,mobilePhone"

# load certificate and thumbprint
with open(client_cert_path, 'rb') as cert_file:
    pkcs12 = crypto.load_pkcs12(cert_file.read(), client_cert_password)

private_key = pkcs12.get_privatekey() \
    .to_cryptography_key()  \
    .private_bytes(
        serialization.Encoding.PEM, 
        serialization.PrivateFormat.PKCS8, 
        serialization.NoEncryption())

thumbprint = pkcs12.get_certificate() \
    .digest('sha1') \
    .decode() \
    .replace(':', '')

# get access token


models.db.connect()


url = ms_graph_resource + '/v1.0/users/delta?$select=jobTitle,department,mobilePhone'

rest_api_service = RestApiService()


organizations = models.Organization.select().where(models.Organization.isAdminConsented)
for organization in organizations:

    print('Sync tenant ' + organization.name)

    data_sync_record, created = models.DataSyncRecord.get_or_create(
        tenantId = organization.tenantId,
        query = users_query)
    
    if created:
        url = ms_graph_resource + '/v1.0' + users_query
    else:
        url = data_sync_record.deltaLink


    authority = aad_instance + organization.tenantId
    auth_context = adal.AuthenticationContext(authority, api_version=None)

    token = auth_context.acquire_token_with_client_certificate(
        ms_graph_resource,
        client_id,
        private_key,
        thumbprint)

    access_token = token['accessToken']

    while True:
        res = rest_api_service.get_json(url, access_token)    
        users = res['value']

        for user in users:
            profile = models.Profile.get_or_none(models.Profile.o365UserId == user['id'])
            if profile:
                profile.jobTitle = user['jobTitle']
                profile.department = user['department']
                profile.mobilePhone = user['mobilePhone']
                print('update user: ' + profile.o365Email)
                profile.save()

        next_link = res.get('@odata.nextLink')
        if next_link:
            url = next_link
        else:
            break;    


    data_sync_record.deltaLink = res.get('@odata.deltaLink')
    data_sync_record.updated = datetime.datetime.now()
    data_sync_record.save()

models.db.close()