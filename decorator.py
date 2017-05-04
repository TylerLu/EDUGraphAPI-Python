'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from django.http import HttpResponseRedirect
from services.auth_service import get_user

def login_required(func):
    def decorator(request, *args, **kwargs):
        user = get_user()
        if not user.get('uid') or not user.get('tenant_id'):
            return HttpResponseRedirect('/Account/Login')
        return func(request, *args, **kwargs)
    return decorator

def admin_only(func):
    def decorator(request, *args, **kwargs):
        user = get_user()
        if user.get('role') != 'Admin':
            return HttpResponseRedirect('/Account/Login')
        return func(request, *args, **kwargs)
    return decorator
