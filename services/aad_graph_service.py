'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import urllib
import constant
from services.rest_api_service import RestApiService

class AADGraphService(object):

    def __init__(self, tenant_id, access_token):
        self.api_base_uri = constant.Resources.AADGraph + tenant_id + '/'
        self.access_token = access_token
        self.rest_api_service = RestApiService()

    def get_service_principal(self):
        app_id = ''
        url = self.api_base_uri + "/servicePrincipals?api-version=1.6&$filter=appId eq '%s'" % constant.client_id
        app_content = self.rest_api_service.get_json(url, self.access_token)
        return app_content['value'][0]

    def delete_service_principal(self, service_principal_id):
        version = '?api-version=1.6'
        url = self.api_base_uri + '/servicePrincipals/%s' % service_principal_id + version
        self.rest_api_service.delete(url, self.access_token)

    def add_app_role_assignments(self, service_principal_id, service_principal_id_name):
        url = self.api_base_uri + '/users?api-version=1.6&$expand=appRoleAssignments'
        users_content = self.rest_api_service.get_json(url, self.access_token)
        users = users_content['value']

        count = 0
        for user in users:
            exist_label = False
            roles = user['appRoleAssignments']
            for role in roles:
                if role['resourceId'] == service_principal_id:
                    exist_label = True
                    break
            if not exist_label:
                data = {
                    'odata.type': 'Microsoft.DirectoryServices.AppRoleAssignment',
                    'principalDisplayName': user['displayName'],
                    'principalId': user['objectId'],
                    'principalType': 'User',
                    'resourceId': service_principal_id,
                    'resourceDisplayName': service_principal_id_name
                }
                count = count+1
                #post_url = self.api_base_uri + '/users/%s' % user['objectId'] + '/appRoleAssignments?api-version=1.6'
                #self.rest_api_service.post_json(post_url, self.access_token, data=data)
