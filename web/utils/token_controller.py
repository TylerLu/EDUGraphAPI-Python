"""
token controller for ms && aad
"""

import datetime
from ..utils import constant
from ..utils.ms_api_request import MSGraphRequest
from ..utils.aad_api_request import AADGraphRequest

class TokenManager(object):
    def __init__(self):
        self._token = ''
        self._refresh_token = ''
        self._resource = ''
        self._expires_on = ''
        
        self._aad_request = AADGraphRequest()
        self._ms_request = MSGraphRequest(constant.client_id, constant.client_secret, constant.authorize_token_uri, constant.graph_base_uri)
    
    def aad_request(self):
        return self._aad_request
    
    def ms_request(self):
        return self._ms_request

    def get_token_by_code(self, code, resource):
        token_result = {}
        if resource == 'aad':
            token_result = self._ms_request.authorize(code, constant.redirect_uri, constant.aad_resource)
        elif resource == 'ms':
            token_result = self._ms_request.authorize(code, constant.redirect_uri, constant.ms_resource)
        else:
            pass
        self._resource = resource
        self._token = token_result.get('accessToken', '')
        self._expires_on = token_result.get('expiresOn', '')
        self._refresh_token = token_result.get('refreshToken', '')
        return self._token

    def _check_valid(self):
        if self._expires_on:
            format_expireson = datetime.datetime.strptime(self._expires_on, "%Y-%m-%d %H:%M:%S.%f")
            current_time = datetime.datetime.now()
            if current_time < format_expireson:
                return True
        return False

    def get_token(self, resource):
        valid = self._check_valid()
        if valid:
            if self._resource == resource:
                return self._token
        try:
            self._update_token(resource)
        except:
            self._token = ''
        return self._token

    def _update_token(self, resource):
        token_result = {}
        if resource == 'aad':
            token_result = self._ms_request.authorize_refresh(self._refresh_token, constant.aad_resource)
        elif resource == 'ms':
            token_result = self._ms_request.authorize_refresh(self._refresh_token, constant.ms_resource)
        else:
            pass
        self._resource = resource
        self._token = token_result.get('accessToken', '')
        self._expires_on = token_result.get('expiresOn', '')
        self._refresh_token = token_result.get('refreshToken', '')
