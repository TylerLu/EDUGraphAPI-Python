'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import urllib
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



