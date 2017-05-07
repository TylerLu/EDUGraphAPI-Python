'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from utils.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin

import os
from services.token_service import RefreshTokenException

class HandleRefreshTokenExceptionMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        context = {}
        context['reason'] = str(exception)
        if exception.__class__.__name__ == 'RefreshTokenException':
            return render(request, 'login0365required.html', context)
        return render(request, 'error.html', context)
