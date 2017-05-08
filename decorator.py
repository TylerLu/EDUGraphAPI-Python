'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from django.http import HttpResponseRedirect
from services.auth_service import AuthService

def login_required(func):
    def decorator(request, *args, **kwargs):
        user = AuthService.get_current_user(request)
        if not user.is_authenticated:
            return HttpResponseRedirect('/Account/Login')
        return func(request, *args, **kwargs)
    return decorator

def admin_only(func):
    def decorator(request, *args, **kwargs):
        user = AuthService.get_current_user(request)
        if not user.is_admin:
            return HttpResponseRedirect('/Account/LogOff')
        return func(request, *args, **kwargs)
    return decorator

def linked_users_only(func):
    def decorator(request, *args, **kwargs):
        user = AuthService.get_current_user(request)
        if not user.are_linked:
            return HttpResponseRedirect('/Link')
        return func(request, *args, **kwargs)
    return decorator

