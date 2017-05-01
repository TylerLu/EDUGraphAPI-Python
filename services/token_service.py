'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
import adal
import datetime
import constant
from account.models import TokenCache

class RefreshTokenException(Exception):
    pass

class TokenService(object):
    '''
    In this sample, tokens are cached in clear text in database. For real projects, they should be encrypted.
    '''
    def __init__(self):
        self._context = adal.AuthenticationContext(constant.authorize_token_uri)

    def get_token_with_code(self, code, redirect_uri, resource):
        result = self._context.acquire_token_with_authorization_code(code, redirect_uri, resource, constant.client_id, constant.client_secret)
        return result

    def get_access_token(self, resource, uid):
        access_token = ''
        token_cache = TokenCache.objects.filter(o365UserId=uid, resource=resource)
        if token_cache:
            token_cache = token_cache[0]
            if self._valid_time(token_cache.expiresOn):
                access_token = token_cache.accessToken
        if not access_token:
            auth_result = self._refresh_token(resource, uid)
            self._create_or_update_token(auth_result)
            access_token = auth_result.get('accessToken')
        return access_token

    def cache_tokens(self, auth_result):
        resource = auth_result['resource']
        self._create_or_update_token(auth_result)
        return auth_result.get('accessToken')

    def _valid_time(self, expires_on):
        format_expireson = datetime.datetime.strptime(expires_on, "%Y-%m-%d %H:%M:%S.%f")
        current_time = datetime.datetime.now()
        format_expireson = format_expireson + datetime.timedelta(minutes=-5)
        if current_time < format_expireson:
            return True
        return False

    def _refresh_token(self, resource, uid):
        token_cache = TokenCache.objects.filter(o365UserId=uid)
        last_time = None
        last_refresh = ''
        for cache in token_cache:
            format_expireson = datetime.datetime.strptime(cache.expiresOn, "%Y-%m-%d %H:%M:%S.%f")
            if not last_time:
                last_time = format_expireson
                last_refresh = cache.refreshToken
            elif format_expireson > last_time:
                last_time = format_expireson
                last_refresh = cache.refreshToken
        try:
            auth_result = self._context.acquire_token_with_refresh_token(last_refresh, constant.client_id, resource, constant.client_secret)
        except:
            raise RefreshTokenException
        return auth_result

    def _create_or_update_token(self, result):
        accessToken = result.get('accessToken', '')
        expiresOn = result.get('expiresOn', '')
        refreshToken = result.get('refreshToken', '')
        resource = result.get('resource', '')
        uid = result.get('oid', '')
        if uid and accessToken and expiresOn and refreshToken and resource:
            token = TokenCache.objects.get_or_create(o365UserId=uid, resource=resource)[0]
            token.accessToken = accessToken
            token.refreshToken = refreshToken
            token.expiresOn = expiresOn
            token.save()
