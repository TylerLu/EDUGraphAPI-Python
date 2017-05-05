'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

import constant
from decorator import login_required
from services.token_service import TokenService
from services.auth_service import get_current_user
from services.education_service import EducationService
from services.local_user_service import LocalUserService

LOCAL_USER = LocalUserService()
TOKEN_SERVICE = TokenService()

@login_required
def aboutme(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user = get_current_user(request)
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user
    if user.local_user.is_authenticated:
        parameter['show_color'] = user.local_user.is_authenticated
        parameter['colors'] = constant.FavoriteColors        
        parameter['favorite_color'] = LOCAL_USER.get_favorite_color(user.user_id)
    if not user.is_admin and user.o365_user is not None:
        token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user.o365_user_id)
        education_service = EducationService(user.tenant_id, token)
        school_id = education_service.get_school_id()
        parameter['groups'] = education_service.get_my_groups(school_id)
    else:
        parameter['groups'] = []
    return render(request, 'managements/aboutme.html', parameter)

@login_required
def updatecolor(request):
    user = get_current_user(request)
    color = request.POST.get('favoritecolor')
    LOCAL_USER.update_favorite_color(color, user.user_id)
    return HttpResponseRedirect('/Manage/AboutMe')