'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from django.http import HttpResponseRedirect

def login_required(func):
    def decorator(request, *args, **kwargs):
        if not request.user or not request.user.get('uid') or not request.user.get('tenant_id'):
            return HttpResponseRedirect('/Account/Login')
        return func(request, *args, **kwargs)
    return decorator

def admin_only(func):
    def decorator(request, *args, **kwargs):
        if request.user.get('role') != 'Admin':
            return HttpResponseRedirect('/Account/Login')
        return func(request, *args, **kwargs)
    return decorator
