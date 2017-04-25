'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from constant import FavoriteColors
from decorator import ms_login_required
from services.token_service import TokenService
from services.user_service import LocalUserService
from services.education_service import SchoolService

LOCAL_USER = LocalUserService()
TOKEN_SERVICE = TokenService()
SCHOOL_SERVICE = SchoolService()

@ms_login_required
def aboutme(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.session['ms_user']
    user_info['showcolor'] = True
    user_info['color'] = LOCAL_USER.get_color(user_info)

    groups = SCHOOL_SERVICE.get_user_groups(user_info['school_id'])

    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['colors'] = FavoriteColors
    parameter['groups'] = groups
    request.session['colors'] = FavoriteColors
    request.session['groups'] = groups
    return render(request, 'managements/aboutme.html', parameter)

def updatecolor(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    # get user info from session
    user_info = request.session['ms_user']
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
