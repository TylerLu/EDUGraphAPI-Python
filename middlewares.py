'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect
 
class TokenErrorMiddleware(MiddlewareMixin):
    
    def process_exception(self, request, exception):
        if str(exception) == 'TokenError':
            return HttpResponseRedirect('/')
