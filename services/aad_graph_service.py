'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
import constant
from services.rest_api_service import RestApiService

class AADGraphService(object):
    
    def __init__(self, method='GET', headers=None):
        self.api_base_uri = 'https://graph.windows.net/canvizEDU.onmicrosoft.com/'
        self.version = '?api-version=1.6'
        self.rest_api_service = RestApiService()
        
    def get_admin_ids(self, token):
        admin_ids = set()
        url = self.api_base_uri + 'directoryRoles' + self.version
        roles_content = self.rest_api_service.get_json(url, token)
        roles_list = roles_content['value']
        id_list = set()
        for role in roles_list:
            if role['displayName'] == constant.company_admin_role_name:
                id_list.add(role['objectId'])
        url = self.api_base_uri + 'directoryRoles/%s/members' + self.version
        for id in id_list:
            members_url = url % id
            members_content = self.rest_api_service.get_json(members_url, token)
            members_list = members_content['value']
            for member in members_list:
                admin_ids.add(member['objectId'])
        return admin_ids

    def get_user_extra_info(self, token):
        sku_ids = set()
        uid = ''
        school_uid = ''
        school_id = ''
        extra_info = {}
        url = self.api_base_uri + 'me' + self.version
        user_content = self.rest_api_service.get_json(url, token)

        uid = user_content['objectId']
        licenses_list = user_content['assignedLicenses']
        for license in licenses_list:
            sku_ids.add(license['skuId'])
        sid = user_content.get('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_StudentId', '')
        tid = user_content.get('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_TeacherId', '')
        if sid:
            school_uid = sid
        elif tid:
            school_uid = tid
        school_id = user_content.get('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId', '')

        extra_info['uid'] = uid
        extra_info['sku_ids'] = sku_ids
        extra_info['school_uid'] = school_uid
        extra_info['school_id'] = school_id
        return extra_info
