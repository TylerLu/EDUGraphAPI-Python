'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import re
import urllib
import constant
from services.rest_api_service import RestApiService

class AADGraphService(object):

    def __init__(self, tenant_id, access_token):
        self.api_base_uri = constant.Resources.AADGraph + '/' + tenant_id + '/'
        self.access_token = access_token
        self.skip_token_re = re.compile('(?<=skiptoken=).*')
        self.rest_api_service = RestApiService()

    def get_service_principal(self):
        url = self.api_base_uri + "servicePrincipals?api-version=1.6&$filter=appId eq '%s'" % constant.client_id
        app_content = self.rest_api_service.get_json(url, self.access_token)
        return next(iter(app_content['value']), None)

    def delete_service_principal(self, service_principal_id):
        version = '?api-version=1.6'
        url = self.api_base_uri + 'servicePrincipals/%s' % service_principal_id + version
        self.rest_api_service.delete(url, self.access_token)

    def add_app_role_assignments(self, service_principal_id, service_principal_id_name):
        count = 0
        url = self.api_base_uri + 'users?api-version=1.6&$expand=appRoleAssignments'
        skip_token = None
        while True:
            url2 = url + '&$skiptoken=' + skip_token if skip_token else url
            users_content = self.rest_api_service.get_json(url2, self.access_token)
            users = users_content['value']
            skip_token = self._get_skip_token(users_content.get('odata.nextLink'))
            for user in users:
                if all(a['resourceId'] != service_principal_id for a in user['appRoleAssignments']):
                    try:
                        self._add_app_role_assignment(user, service_principal_id, service_principal_id_name)
                        count = count + 1
                    except:
                        pass
            if skip_token == None:
                break;           
        return count

    def _add_app_role_assignment(self, user, service_principal_id, service_principal_id_name):
        app_role_assignment = {
            'odata.type': 'Microsoft.DirectoryServices.AppRoleAssignment',
            'principalDisplayName': user['displayName'],
            'principalId': user['objectId'],
            'principalType': 'User',
            'resourceId': service_principal_id,
            'resourceDisplayName': service_principal_id_name
        }
        post_url = self.api_base_uri + 'users/%s' % user['objectId'] + '/appRoleAssignments?api-version=1.6'
        self.rest_api_service.post_json(post_url, self.access_token, data=app_role_assignment)
              
    def _get_skip_token(self, nextlink):
        if nextlink:
            matches = self.skip_token_re.findall(nextlink)
            if matches:
                return matches[0]
        return None