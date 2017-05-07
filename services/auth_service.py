'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import urllib
import constant
import uuid
import jwt
import requests
from models.auth import O365User, UnifiedUser

class AuthService(object):

    @staticmethod
    def get_redirect_uri(request, relative_redirect_uri):
        scheme = request.scheme
        host = request.get_host()
        return '%s://%s/%s' % (scheme, host, relative_redirect_uri)

    @staticmethod
    def get_authorization_url(request, response_type, relative_redirect_uri, state, extra_params = None):
        params  = {
            'client_id' : constant.client_id,
            'response_type': response_type,
            'response_mode': 'form_post',
            'redirect_uri': AuthService.get_redirect_uri(request, relative_redirect_uri),
            'state': state
            }
        if extra_params:
            params.update(extra_params)
        request.session['auth_state'] = state
        nonce = params.get('nonce')
        if nonce:
            request.session['auth_nonce'] = nonce
        return constant.login_base_uri + urllib.parse.urlencode(params).replace('%2B', '+')

    @staticmethod
    def get_random_string():
        return uuid.uuid4().hex

    @staticmethod
    def validate_state(request):
        if request.POST.get('state') != request.session.get('auth_state'):
            raise Exception('state does not match')

    @staticmethod
    def get_id_token(request):
        id_token = request.POST.get('id_token')
        return jwt.decode(id_token, verify=False)

    @staticmethod
    def get_current_user(request):
        return UnifiedUser(request)

    @staticmethod
    def set_o365_user(request, o365_user):
        request.session[constant.o365_user_session_key] = o365_user.to_json()

    @staticmethod
    def clear_o365_user(request):
        if constant.o365_user_session_key in request.session:
            del request.session[constant.o365_user_session_key]
