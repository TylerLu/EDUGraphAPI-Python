import constants
import datetime

from authentication_helper import AuthenticationHelper
from models import database, Organization, DataSyncRecord, Profile
from ms_graph import GraphServiceClient

class UserDataSyncService(object):

    def __init__(self):
        self._users_query = "users"
        self._auth_helper = AuthenticationHelper(constants.client_cert_path, constants.client_cert_password)
    
    def sync(self):
        for organization in Organization.get_consented():
            self.sync_organization(organization)

    def sync_organization(self, organization):
        print('Sync tenant ' + organization.name)    

        client = self._get_graph_service_client(organization.tenantId)

        record, is_new_record = DataSyncRecord.get_or_create(
            tenantId = organization.tenantId,
            query = self._users_query)

        if is_new_record:
            query = { '$select': 'jobTitle,department,mobilePhone' }
            users, next_link, delta_link = client.get_users_delta(query)
        else:
            users, next_link, delta_link = client.get_users(record.deltaLink)

        while True:
            for user in users:
                profile = Profile.get_or_none(Profile.o365UserId == user['id'])
                if profile:
                    self._update_profile(profile, user)
            if next_link:
                users, next_link, delta_link = client.get_users(next_link)
            else:
                break

        self._update_data_sync_record(record, delta_link)

    def _update_profile(self, profile, user):
        print('update user: ' + profile.o365Email)
        profile.jobTitle = user['jobTitle']
        profile.department = user['department']
        profile.mobilePhone = user['mobilePhone']
        profile.save()

    def _update_data_sync_record(self, record, delta_link):
        record.deltaLink = delta_link
        record.updated = datetime.datetime.now()
        record.save()

    def _get_graph_service_client(self, tenant_id):        
        access_token = self._auth_helper.get_app_only_access_token(
            tenant_id, constants.client_id, constants.ms_graph_resource)
        return GraphServiceClient(constants.ms_graph_resource, access_token)