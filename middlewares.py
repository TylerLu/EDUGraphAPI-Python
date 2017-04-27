'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
 
class AppErrorMiddleware(MiddlewareMixin):
    
    def process_exception(self, request, exception):
        if str(exception) == 'TokenError':
            return HttpResponseRedirect('/')

        return render(request, 'error.html', {'message':str(exception)})
