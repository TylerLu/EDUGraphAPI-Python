"""
token controller for ms && aad
"""

import datetime
import constant
from utils.ms_api_request import MSGraphRequest

class TokenManager(object):
    def __init__(self):
        self._ms_request = MSGraphRequest()
    
    def get_token_by_code(self, code, resource, redirect_uri):
        token_result = {}
        if resource == 'aad':
            token_result = self._ms_request.authorize(code, redirect_uri, constant.aad_resource)
        elif resource == 'ms':
            token_result = self._ms_request.authorize(code, redirect_uri, constant.ms_resource)
        else:
            pass
        token = token_result.get('accessToken', '')
        expires_on = token_result.get('expiresOn', '')
        refresh_token = token_result.get('refreshToken', '')
        return token, refresh_token, expires_on

    def check(self, expires_on):
        format_expireson = datetime.datetime.strptime(expires_on, "%Y-%m-%d %H:%M:%S.%f")
        current_time = datetime.datetime.now()
        if current_time < format_expireson:
            return True
        return False

    def get_token(self, refresh_token, resource):
        token_result = {}
        if resource == 'aad':
            token_result = self._ms_request.authorize_refresh(refresh_token, constant.aad_resource)
        elif resource == 'ms':
            token_result = self._ms_request.authorize_refresh(refresh_token, constant.ms_resource)
        else:
            pass
        token = token_result.get('accessToken', '')
        expires_on = token_result.get('expiresOn', '')
        refresh_token = token_result.get('refreshToken', '')
        return token, refresh_token, expires_on
