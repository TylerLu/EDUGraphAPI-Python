'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
import adal
import datetime
import constant
from account.models import TokenCache

class tokenAccessError(Exception):
    pass

class TokenService(object):
    '''
    In this sample, tokens are cached in clear text in database. For real projects, they should be encrypted.
    '''
    def __init__(self):
        self._context = adal.AuthenticationContext(constant.authorize_token_uri)

    def code(self, value):
        self.code = value
    
    def redirect_uri(self, value):
        self.redirect_uri = value
    
    def authorize(self, resource):
        result = self._context.acquire_token_with_authorization_code(self.code, self.redirect_uri, resource, constant.client_id, constant.client_secret)
        return result
    
    def get_access_token(self, resource, uid):
        access_token = ''
        try:
            token_cache = TokenCache.objects.get(o365UserId=uid, resource=resource)
            if self._valid_time(token_cache.expiresOn):
                access_token = token_cache.accessToken
            else:
                token_result = self._refresh_token(resource, uid)
                self._create_or_update_token(token_result, resource)
                access_token = token_result.get('accessToken')
        except:
            raise tokenAccessError('TokenError')
        return access_token

    def set_access_token(self, resource):
        token_result = self.authorize(resource)
        self._create_or_update_token(token_result, resource)
        return  token_result.get('accessToken')
    
    def _valid_time(self, expires_on):
        format_expireson = datetime.datetime.strptime(expires_on, "%Y-%m-%d %H:%M:%S.%f")
        current_time = datetime.datetime.now()
        format_expireson = format_expireson + datetime.timedelta(minutes=-5)
        if current_time < format_expireson:
            return True
        return False

    def _refresh_token(self, resource, uid):
        token_cache = TokenCache.objects.get(o365UserId=uid, resource=resource)
        refresh_token = token_cache.refreshToken
        result = self._context.acquire_token_with_refresh_token(refresh_token, constant.client_id, resource, constant.client_secret)
        return result

    def _create_or_update_token(self, result, resource):
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
