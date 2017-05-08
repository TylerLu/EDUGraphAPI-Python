'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from models.db import Profile
from utils.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from services.auth_service import AuthService

import os
from services.token_service import RefreshTokenException

class HandleRefreshTokenExceptionMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        context = { 
            'user': AuthService.get_current_user(request),
            'reason': str(exception)
        }
        if exception.__class__.__name__ == 'RefreshTokenException':
            return render(request, 'login0365required.html', context)


class UserUnlinkMonitorMiddleware(MiddlewareMixin):
    '''
    This middleware will clear o365 user from session, once if detects an unlink (mostly made by admins).
    '''
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = AuthService.get_current_user(request)
        if user.are_linked:
            if not Profile.objects.filter(id=user.user_id, o365UserId=user.o365_user_id):
                AuthService.clear_o365_user(request)
        return self.get_response(request)