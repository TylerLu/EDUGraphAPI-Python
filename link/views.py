'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.conf import settings

from services.local_user_service import LocalUserService

from decorator import ms_login_required

from .forms import CreateLocalInfo, LoginLocalInfo

LOCAL_USER = LocalUserService()

@ms_login_required
def link(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.session['ms_user']
    # set parameter for template
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    return render(request, 'link/index.html', parameter)

@ms_login_required
def createlocal(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.session['ms_user']
    create_local_form = CreateLocalInfo()
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['create_local_form'] = create_local_form
    errors = []
    # POST /link/createlocal
    if request.method == 'POST':
        create_local_form = CreateLocalInfo(request.POST)
        if create_local_form.is_valid():
            data = create_local_form.clean()
            favoritecolor = data['FavoriteColor']
            user_info['color'] = favoritecolor
        ret = LOCAL_USER.create(user_info)
        LOCAL_USER.update_role(user_info['uid'], user_info['role'])
        if not ret:
            errors.append('Name %s is already taken.' % user_info['mail'])
            errors.append("Email '%s' is already taken." % user_info['mail'])
            parameter['errors'] = errors
            return render(request, 'link/createlocal.html', parameter)
        else:
            user_info['arelinked'] = True
            user_info['email'] = user_info['mail']
            user_info['o365Email'] = user_info['mail']
            request.session['ms_user'] = user_info
            return HttpResponseRedirect('/Schools')
    # GET /link/createlocal
    else:
        return render(request, 'link/createlocal.html', parameter)

@ms_login_required
def loginlocal(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.session['ms_user']
    login_local_form = LoginLocalInfo()
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['login_local_form'] = login_local_form
    errors = []
    # POST /link/loginlocal
    if request.method == 'POST':
        login_local_form = LoginLocalInfo(request.POST)
        if login_local_form.is_valid():
            data = login_local_form.clean()
            email = data['Email']
            password = data['Password']
            user = authenticate(username=email, password=password)
            if user is not None:
                user_info = request.session['ms_user']
                LOCAL_USER.link(user_info, data)
                user_info['arelinked'] = True
                user_info['email'] = email
                user_info['o365Email'] = user_info['mail']
                request.session['ms_user'] = user_info
                return HttpResponseRedirect('/Schools')
            else:
                errors.append('Invalid login attempt.')
                parameter['errors'] = errors
                return render(request, 'link/loginlocal.html', parameter)
    # GET /link/loginlocal
    else:
        return render(request, 'link/loginlocal.html', parameter)
