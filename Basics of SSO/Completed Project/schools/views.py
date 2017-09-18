'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import json
from utils.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from decorator import login_required

from services.auth_service import AuthService

 


@login_required
def schools(request):   
    user = AuthService.get_current_user(request)
 
    context = {
        'user': user
    }
    return render(request, 'schools/index.html', context)

