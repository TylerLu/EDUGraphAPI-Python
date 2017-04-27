'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
import adal
import datetime
import constant
from account.models import TokenCache

def singleton(cls, *args, **kw):    
    instances = {}    
    def _singleton():    
        if cls not in instances:    
            instances[cls] = cls(*args, **kw)    
        return instances[cls]    
    return _singleton    
  
class tokenAccessError(Exception):
    pass

@singleton    
class TokenService(object):
    
    def __init__(self):
        self._code = ''
        self._redirect_uri = ''
        self._access_token = ''
        self._refresh_token = ''
        self._expires_on = ''
        self._resource = ''
        self._map = constant.token_source
        self._context = adal.AuthenticationContext(constant.authorize_token_uri)

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value
    
    @property
    def redirect_uri(self):
        return self._redirect_uri

    @redirect_uri.setter
    def redirect_uri(self, value):
        self._redirect_uri = value
    
    def authorize(self, resource):
        result = self._context.acquire_token_with_authorization_code(self._code, self._redirect_uri, resource, constant.client_id, constant.client_secret)
        return result
    
    def authorize_refresh(self, resource):
        result = self._context.acquire_token_with_refresh_token(self._refresh_token, constant.client_id, resource, constant.client_secret)
        return result

    def _get_token_by_refresh(self, resource):
        try:
            token_result = self.authorize_refresh(self._map[resource])
            return token_result
        except:
            raise tokenAccessError('TokenError')
    
    def _update_token_to_db(self, result, resource):
        accessToken = result.get('accessToken', '')
        expiresOn = result.get('expiresOn', '')
        refreshToken = result.get('refreshToken', '')
        uid = result.get('oid', '')
        if uid and accessToken and expiresOn and refreshToken:
            token = TokenCache.objects.get_or_create(o365UserId=uid, resource=resource)[0]
            token.accessToken = accessToken
            token.refreshToken = refreshToken
            token.expiresOn = expiresOn
            token.save()
        
    def _get_token_by_code(self, resource):
        try:
            token_result = self.authorize(self._map[resource])
            return token_result
        except:
            raise tokenAccessError('TokenError')
    
    def _valid_time(self, expires_on):
        format_expireson = datetime.datetime.strptime(expires_on, "%Y-%m-%d %H:%M:%S.%f")
        current_time = datetime.datetime.now()
        if current_time < format_expireson:
            return True
        return False

    def _check_token(self, resource):
        if self._access_token and self._refresh_token and self._expires_on and self._resource:
            if self._resource != resource:
                return False, 'diff'
            if self._valid_time(self._expires_on):
                return True, ''
            else:
                return False, 'past'
        return False, 'empty'

    def get_access_token(self, resource):
        out_token = ''
        if not self._code:
            raise tokenAccessError('TokenError')
        if not self._redirect_uri:
            raise tokenAccessError('TokenError')
        ret, reason = self._check_token(resource)
        if not ret:
            if reason == 'diff':
                if self._valid_time(self._expires_on):
                    token_result = self._get_token_by_refresh(resource)
                else:
                    token_result = self._get_token_by_code(resource)
            if reason == 'empty' or reason == 'past':
                token_result = self._get_token_by_code(resource)
            if token_result:
                self._update_token_to_db(token_result, resource)
                self._access_token = token_result.get('accessToken', '')
                self._expires_on = token_result.get('expiresOn', '')
                self._refresh_token = token_result.get('refreshToken', '')
                self._resource = resource
        out_token = self._access_token
        return out_token


        

