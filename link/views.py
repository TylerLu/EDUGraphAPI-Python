'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate as auth_authenticate
from django.conf import settings

import constant
from decorator import login_required
from services.auth_service import login
from services.token_service import TokenService
from services.ms_graph_service import MSGraphService
from services.aad_graph_service import AADGraphService
from services.o365_user_service import O365UserService
from services.local_user_service import LocalUserService

from .forms import CreateLocalInfo, LoginLocalInfo

LOCAL_USER = LocalUserService()
TOKEN_SERVICE = TokenService()

@login_required
def link(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.user
    # set parameter for template
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    return render(request, 'link/index.html', parameter)

@login_required
def createlocal(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.user
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

@login_required
def loginlocal(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.user
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
            user = auth_authenticate(username=email, password=password)
            if user is not None:
                ret = LOCAL_USER.link(user_info, data)
                if ret:
                    user_info['arelinked'] = True
                    user_info['email'] = email
                    user_info['o365Email'] = user_info['mail']
                    login(request, user_info)
                    return HttpResponseRedirect('/Schools')
            errors.append('Invalid login attempt.')
            parameter['errors'] = errors
            return render(request, 'link/loginlocal.html', parameter)
    # GET /link/loginlocal
    else:
        return render(request, 'link/loginlocal.html', parameter)

def login_o365(request):
    scheme = request.scheme
    host = request.get_host()
    redirect_uri = '%s://%s/link/ProcessCode' % (scheme, host)
    auth_url = constant.o365_login_url + redirect_uri
    return HttpResponseRedirect(auth_url)

def processcode(request):
    scheme = request.scheme
    host = request.get_host()
    redirect_uri = '%s://%s/link/ProcessCode' % (scheme, host)
    code = request.GET.get('code', '')

    aad_auth_result = TOKEN_SERVICE.get_token_with_code(code, redirect_uri, constant.Resources.AADGraph)
    aad_token = TOKEN_SERVICE.cache_tokens(aad_auth_result)

    ms_auth_result = TOKEN_SERVICE.get_token_with_code(code, redirect_uri, constant.Resources.MSGraph)
    ms_token = TOKEN_SERVICE.cache_tokens(ms_auth_result)

    ms_graph_service = MSGraphService(token=ms_token)
    ms_client = ms_graph_service.get_client()

    o365_user_service = O365UserService()
    client_user = o365_user_service.get_client_user(ms_client)

    aad_graph_service = AADGraphService(client_user['tenant_id'], aad_token)
    admin_ids = aad_graph_service.get_admin_ids()
    extra_user = aad_graph_service.get_user_extra_info()

    user_info = o365_user_service.get_user(client_user, admin_ids, extra_user)

    LOCAL_USER.create_organization(user_info)

    if not user_info.get('arelinked', False):
        if user_info.get('localexisted') and user_info['mail'] != request.user['mail']:
            return HttpResponseRedirect('/')
        ret = LOCAL_USER.link_o365(request.user, user_info)
        if ret:
            user_info['arelinked'] = True
            request.user.pop('uid')
            request.user.pop('tenant_id')
            request.user.pop('arelinked')
            user_info.update(request.user)
            login(request, user_info)
            if user_info['role'] != 'Admin':
                return HttpResponseRedirect('/Schools')
            else:
                return HttpResponseRedirect('/Admin')

    return HttpResponseRedirect('/')

