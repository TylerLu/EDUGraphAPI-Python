'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import msgraph
import constant
from utils.auth_provider import AuthProvider
from services.rest_api_service import RestApiService
from models.auth import O365User
from models.education import Document, Conversation

class MSGraphService(object):

    def __init__(self, access_token):
        self.access_token = access_token
        self.api_base_uri = constant.Resources.MSGraph + 'v1.0' + '/'
        self.rest_api_service = RestApiService()

        auth_provider = AuthProvider()
        auth_provider.access_token(self.access_token)
        self.ms_graph_client = msgraph.GraphServiceClient(self.api_base_uri, auth_provider, msgraph.HttpProvider())

    def get_o365_user(self, tenant_id):
        me = self._get_me().to_dict()
        org = self._get_organization(tenant_id)

        id = me['id']
        first_name = me['givenName']
        last_name = me['surname']
        display_name = me['displayName']
        email = me['mail']
        if not email:
            email = me['userPrincipalName']
        tenant_name = org['displayName']
        roles = self._get_roles(id)
        return O365User(id, email, first_name, last_name, display_name, tenant_id, tenant_name, roles)

    def get_photo(self, object_id):
        url = self.api_base_uri + 'users/%s/photo/$value' % object_id
        try:
            return self.rest_api_service.get_img(url, self.access_token)
        except:
            return None

    def get_documents(self, object_id):
        url = self.api_base_uri + 'groups/%s/drive/root/children' % object_id
        return self.rest_api_service.get_object_list(url, self.access_token, model=Document)

    def get_documents_root(self, object_id):
        url = self.api_base_uri + 'groups/%s/drive/root' % object_id
        document = self.rest_api_service.get_object(url, self.access_token, model=Document)
        return document.web_url

    def get_conversations(self, object_id):
        url = self.api_base_uri + 'groups/%s/conversations' % object_id
        return self.rest_api_service.get_object_list(url, self.access_token, model=Conversation)
    
    def get_conversations_url(self, conversation_id, section_email):
        return 'https://outlook.office.com/owa/?path=/group/%s/mail&exsvurl=1&ispopout=0&ConvID=%s' % (section_email, conversation_id, )

    def get_conversations_root(self, section_email):
        return 'https://outlook.office.com/owa/?path=/group/%s/mail&exsvurl=1&ispopout=0' % section_email

    def _get_roles(self, user_id):
        roles = []
        # check if the user is an admin
        directory_roles = self._get_directory_roles()
        admin_role = next(r for r in directory_roles if r.display_name == constant.company_admin_role_name)
        if admin_role:
            members = admin_role.to_dict()['members']
            if any(m for m in members if m['id']==user_id):
                roles.append(constant.Roles.Admin)
        # check if the user is a faculty or a student
        assigned_licenses = self._get_assigned_licenses()
        for license in assigned_licenses:
            license_id = license['skuId']
            if license_id == constant.O365ProductLicenses.Faculty or license_id == constant.O365ProductLicenses.FacultyPro:
                roles.append(constant.Roles.Faculty)
            if license_id == constant.O365ProductLicenses.Student or license_id == constant.O365ProductLicenses.StudentPro:
                roles.append(constant.Roles.Student)
        return roles

    def _get_me(self):
        return self.ms_graph_client.me.get()

    def _get_assigned_licenses(self):
        url = self.api_base_uri + 'me/assignedLicenses'
        return self.rest_api_service.get_json(url, self.access_token)['value']

    def _get_organization(self, tenant_id):
        url = self.api_base_uri + 'organization/' + tenant_id
        return self.rest_api_service.get_json(url, self.access_token)


    def _get_directory_roles(self):
        expand_members = msgraph.options.QueryOption('$expand', 'members')
        return self.ms_graph_client.directory_roles.request(options=[expand_members]).get()