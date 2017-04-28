'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
 
import os

class AppErrorMiddleware(MiddlewareMixin):
    
    def process_exception(self, request, exception):
        if str(exception) == 'TokenError':
            scheme = request.scheme
            host = request.get_host()
            url = self._o365_login(scheme, host)
            return HttpResponseRedirect(url)

        #return render(request, 'error.html', {'message':str(exception)})
    
    def _o365_login(self, scheme, host):
        client_id = os.environ['ClientId']
        redirect_uri = '%s://%s/MS/Login' % (scheme, host)
        base_uri = 'https://login.microsoftonline.com/common/oauth2/authorize?'
        signin_url = base_uri + 'response_type=code&client_id=%s&redirect_uri=%s' % (client_id, redirect_uri)
        return signin_url
