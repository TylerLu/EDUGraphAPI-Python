'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
from django.http import HttpResponseRedirect

def ms_login_required(func):
    def decorator(request, *args, **kwargs):
        if not request.session['ms_user']:
            return HttpResponseRedirect('/Account/Login')
        return func(request, *args, **kwargs)  
    return decorator  

