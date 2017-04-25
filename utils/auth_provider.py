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
        """
        Sets the access_token for the AuthProvider
        Returns:
            str: The access token
        """
        self.__access_token = value

    def authenticate_request(self, request):
        """Append the required authentication headers
        to the specified request. This will only function
        if a session has been successfully created using
        :func:`authenticate`. This will also refresh the
        authentication token if necessary.

        Args:
            request (:class:`RequestBase<microsoft.request_base.RequestBase>`):
                The request to authenticate
        """
        key = 'Authorization'
        value = 'Bearer {0}'.format(self.__access_token)
        option = HeaderOption(key, value)
        request.append_option(option)
        key = 'Accept'
        value = 'application/json'
        option = HeaderOption(key, value)
        request.append_option(option)
        key = 'Content-Type'
        value = 'application/json'
        option = HeaderOption(key, value)
        request.append_option(option)

    def refresh_token(self):
        """Refresh the token currently used by the session"""
        pass
