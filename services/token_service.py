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
    This class is responsible for cache and retrieve tokens to and from the backend database.
    In this sample, tokens are cached in clear text in database. For real projects, they should be encrypted.
    '''
    def __init__(self):
        pass

    def get_token_with_code(self, code, redirect_uri, resource):
        auth_context = adal.AuthenticationContext(constant.authorize_token_uri)
        result = auth_context.acquire_token_with_authorization_code(code, redirect_uri, resource, constant.client_id, constant.client_secret)
        return result

    def get_access_token(self, resource, o365_user_id):
        '''
        Get access token.
        If the cached token is exipred, a new refresh token will be got with the refresh token, cached and returned to the invoker.
        If there is no refresh token or the refresh token is expired, RefreshTokenException will be raised.
        '''
        token_cache = TokenCache.objects.filter(o365UserId=o365_user_id, resource=resource).first()
        if token_cache and self._is_valid(token_cache.expiresOn):
            return token_cache.accessToken

        auth_result = self._refresh_token(resource, o365_user_id)
        self._create_or_update_token(auth_result, o365_user_id)
        return auth_result.get('accessToken')

    def cache_tokens(self, auth_result, o365_user_id):
        '''
        Cache access token and refresh token.
        '''
        self._create_or_update_token(auth_result, o365_user_id)
        return auth_result.get('accessToken')

    def _is_valid(self, expires_on):
        now = datetime.datetime.now(expires_on.tzinfo)
        return now < expires_on - datetime.timedelta(minutes=5)

    def _refresh_token(self, resource, o365_user_id):
        cache = TokenCache.objects.filter(o365UserId=o365_user_id).order_by('-expiresOn').first()
        if cache is None:
            raise RefreshTokenException('cache is None')
        try:
            auth_context = adal.AuthenticationContext(constant.authorize_token_uri)
            auth_result = auth_context.acquire_token_with_refresh_token(cache.refreshToken, constant.client_id, resource, constant.client_secret)
        except:
            raise RefreshTokenException('refresh is Error')
        return auth_result

    def _create_or_update_token(self, auth_result, o365UserId):
        accessToken = auth_result.get('accessToken', '')
        expiresOn =  auth_result.get('expiresOn', '')
        refreshToken = auth_result.get('refreshToken', '')
        resource = auth_result.get('resource', '')
        if accessToken and expiresOn and refreshToken and resource:
            token = TokenCache.objects.get_or_create(o365UserId=o365UserId, resource=resource)[0]
            token.accessToken = accessToken
            token.refreshToken = refreshToken
            token.expiresOn = expiresOn
            token.save()
