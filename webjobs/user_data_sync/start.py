import constants

import datetime


from rest_api_service import RestApiService
import models 

from authentication_helper import AuthenticationHelper


users_query = "/users/delta?$select=jobTitle,department,mobilePhone"

authentication_helper = AuthenticationHelper(constants.client_cert_path, constants.client_cert_password)

models.db.connect()


url = constants.ms_graph_resource + '/v1.0/users/delta?$select=jobTitle,department,mobilePhone'

rest_api_service = RestApiService()


organizations = models.Organization.select().where(models.Organization.isAdminConsented)
for organization in organizations:

    print('Sync tenant ' + organization.name)

    data_sync_record, created = models.DataSyncRecord.get_or_create(
        tenantId = organization.tenantId,
        query = users_query)
    
    if created:
        url = constants.ms_graph_resource + '/v1.0' + users_query
    else:
        url = data_sync_record.deltaLink

    access_token = authentication_helper.get_app_only_access_token(
        organization.tenantId,
        constants.client_id,
        constants.ms_graph_resource)

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