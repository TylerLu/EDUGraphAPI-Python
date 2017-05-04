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
