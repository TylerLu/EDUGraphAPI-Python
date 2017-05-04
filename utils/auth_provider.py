'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''

import adal
import requests
import msgraph
from msgraph.options import HeaderOption
from msgraph.auth_provider_base import AuthProviderBase


class AuthProvider(AuthProviderBase):
    
    def __init__(self):
        self.__access_token = ''

    def access_token(self, value):
        self.__access_token = value

    def authenticate_request(self, request):   
        request.append_option(HeaderOption('Authorization', 'Bearer {0}'.format(self.__access_token)))
        request.append_option(HeaderOption('Accept', 'application/json'))
        request.append_option(HeaderOption('Content-Type', 'application/json'))

    def refresh_token(self):
        """
        No need to refresh token. The other parts of the app ensure that the access token is invalid.
        """
        pass
