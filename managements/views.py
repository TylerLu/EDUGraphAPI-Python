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
from services.auth_service import login, get_user
from services.education_service import EducationService
from services.local_user_service import LocalUserService

LOCAL_USER = LocalUserService()
TOKEN_SERVICE = TokenService()

@login_required
def aboutme(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = get_user()
    user_info['show_color'] = True
    user_info['color'] = LOCAL_USER.get_color(user_info)
    login(user_info)

    if user_info['role'] != 'Admin' and user_info['school_id']:
        token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user_info['uid'])
        education_service = EducationService(user_info['tenant_id'], token)
        groups = education_service.get_my_groups(user_info['school_id'])
    else:
        groups = []

    user_info = get_user()
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['colors'] = constant.FavoriteColors
    parameter['groups'] = groups
    request.session['colors'] = constant.FavoriteColors
    request.session['groups'] = groups
    return render(request, 'managements/aboutme.html', parameter)

def updatecolor(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    # get user info from session
    user_info = get_user()
    color = request.POST.get('favoritecolor')
    LOCAL_USER.update_color(color, user_info)
    user_info['color'] = LOCAL_USER.get_color(user_info)
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['colors'] = request.session['colors']
    parameter['groups'] = request.session['groups']
    parameter['savemessage'] = "<span class='saveresult'>Favorite color has been updated!</span>"
    return render(request, 'managements/aboutme.html', parameter)
