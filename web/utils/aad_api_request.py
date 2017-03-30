"""
AAD Graph Api Request Class
"""

import json
import requests
from ..utils import constant

class AADGraphRequest(object):
    
    def __init__(self, method='GET', headers=None, token=''):
        self._base_uri = 'https://graph.windows.net/canvizEDU.onmicrosoft.com/'
        self._method = method
        self._headers = headers
        self._headers = {'Accept': 'application/json',
                         'Content-Type': 'application/json'}
        if headers:
            self._headers.update(headers)

        self._access_token = token

    def set_method(self, value):
        self._method = value

    def set_headers(self, value):
        self._headers = value
    
    def set_access_token(self, value):
        self._access_token = value

    def send(self, url, token):
        key = 'Authorization'
        value = 'Bearer {0}'.format(token)
        self._headers[key] = value
        session = requests.Session()
        request_url = self._base_uri + url + '?api-version=1.6'
        request = requests.Request(self._method, request_url, self._headers)
        prepped = request.prepare()
        response = session.send(prepped)
        content = ''
        if response.status_code == 200:
            content = json.loads(response.text)
        return content
    
    def get_admin_ids(self, token):
        admin_ids = set()
        try:
            url = 'directoryRoles'
            roles_content = self.send(url, token)
            roles_list = roles_content['value']
            id_list = set()
            for role in roles_list:
                if role['displayName'] == constant.company_admin_role_name:
                    id_list.add(role['objectId'])
            url = 'directoryRoles/%s/members'
            for id in id_list:
                members_url = url % id
                members_content = self.send(members_url, token)
                members_list = members_content['value']
                for member in members_list:
                    admin_ids.add(member['objectId'])
        except:
            pass
        return admin_ids
