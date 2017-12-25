'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import constant
from utils.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

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
    login_as =""
    if user.local_user.is_authenticated:
        context['show_color'] = user.local_user.is_authenticated
        context['colors'] = constant.favorite_colors        
        context['favorite_color'] = user_service.get_favorite_color(user.user_id)
    if user.is_admin:
        login_as ="Admin"
    if not user.is_admin and user.o365_user is not None:
        token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)        
        education_service = EducationService(user.tenant_id, token)            
        me = education_service.get_me() 
        my_school_id = me.schools[0].id
        
        if me.is_teacher:
            login_as="Teacher"
        if me.is_student:
            login_as="Student"
        
        context['me'] = me
        context['groups'] = education_service.get_my_classes(my_school_id)
    else:
        context['groups'] = []
    context['login_as'] = login_as
    context['role']=login_as
    return render(request, 'managements/aboutme.html', context)

@login_required
def updatecolor(request):
    user = AuthService.get_current_user(request)
    color = request.POST.get('favoritecolor')
    user_service.update_favorite_color(color, user.user_id)
    request.session["Message"] = "Favorite color has been updated!"
    return HttpResponseRedirect('/Manage/AboutMe')