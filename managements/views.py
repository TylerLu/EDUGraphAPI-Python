'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from utils.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

import constant
from decorator import login_required
from services.token_service import TokenService
from services.auth_service import AuthService
from services.education_service import EducationService
from services.user_service import UserService

user_service = UserService()
token_service = TokenService()

@login_required
def aboutme(request):
    user = AuthService.get_current_user(request)
    context = { 'user': user }
    if user.local_user.is_authenticated:
        context['show_color'] = user.local_user.is_authenticated
        context['colors'] = constant.FavoriteColors        
        context['favorite_color'] = user_service.get_favorite_color(user.user_id)
    if not user.is_admin and user.o365_user is not None:
        token = token_service.get_access_token(constant.Resources.AADGraph, user.o365_user_id)
        education_service = EducationService(user.tenant_id, token)
        my_school_id = education_service.get_my_school_id()
        context['groups'] = education_service.get_my_sections(my_school_id)
    else:
        context['groups'] = []
    return render(request, 'managements/aboutme.html', context)

@login_required
def updatecolor(request):
    user = AuthService.get_current_user(request)
    color = request.POST.get('favoritecolor')
    user_service.update_favorite_color(color, user.user_id)
    return HttpResponseRedirect('/Manage/AboutMe')