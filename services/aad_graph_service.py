'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
import constant
from services.rest_api_service import RestApiService

class AADGraphService(object):

    def __init__(self, tenant_id, token):
        self.api_base_uri = constant.Resources.AADGraph + tenant_id + '/'
        self.token = token
        self.rest_api_service = RestApiService()

    def get_admin_ids(self):
        admin_ids = set()
        version = '?api-version=1.6'
        url = self.api_base_uri + 'directoryRoles' + version
        roles_content = self.rest_api_service.get_json(url, self.token)
        roles_list = roles_content['value']
        id_list = set()
        for role in roles_list:
            if role['displayName'] == constant.company_admin_role_name:
                id_list.add(role['objectId'])
        url = self.api_base_uri + 'directoryRoles/%s/members' + version
        for id in id_list:
            members_url = url % id
            members_content = self.rest_api_service.get_json(members_url, self.token)
            members_list = members_content['value']
            for member in members_list:
                admin_ids.add(member['objectId'])
        return admin_ids

    def get_license_ids(self):
        sku_ids = set()
        version = '?api-version=1.6'
        url = self.api_base_uri + 'me' + version
        user_content = self.rest_api_service.get_json(url, self.token)
        licenses_list = user_content['assignedLicenses']
        for license in licenses_list:
            sku_ids.add(license['skuId'])
        return sku_ids

    def get_app_id(self):
        app_id = ''
        url = self.api_base_uri + "/servicePrincipals?api-version=1.6&$filter=appId eq '%s'" % constant.client_id
        app_content = self.rest_api_service.get_json(url, self.token)
        app_id = app_content['value'][0]['objectId']
        return app_id

    def delete_app(self, app_id):
        version = '?api-version=1.6'
        url = self.api_base_uri + '/servicePrincipals/%s' % app_id + version
        self.rest_api_service.delete(url, self.token)

    def get_app_name(self):
        app_name = ''
        url = self.api_base_uri + "/servicePrincipals?api-version=1.6&$filter=appId eq '%s'" % constant.client_id
        app_content = self.rest_api_service.get_json(url, self.token)
        app_name = app_content['value'][0]['appDisplayName']
        return app_name

    def add_app_users(self, app_id, app_name):
        url = self.api_base_uri + '/users?api-version=1.6&$expand=appRoleAssignments'
        users_content = self.rest_api_service.get_json(url, self.token)
        users = users_content['value']
        for user in users:
            exist_label = False
            roles = user['appRoleAssignments']
            for role in roles:
                if role['resourceId'] == app_id:
                    exist_label = True
                    break
            if not exist_label:
                data = {
                    'odata.type': 'Microsoft.DirectoryServices.AppRoleAssignment',
                    'principalDisplayName': user['displayName'],
                    'principalId': user['objectId'],
                    'principalType': 'User',
                    'resourceId': app_id,
                    'resourceDisplayName': app_name
                }
                #post_url = self.api_base_uri + '/users/%s' % user['objectId'] + '/appRoleAssignments?api-version=1.6'
                #self.rest_api_service.post_json(post_url, self.token, data=data)
