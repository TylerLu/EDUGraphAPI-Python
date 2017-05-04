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
from services.token_service import TokenService
from services.auth_service import login, get_user
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
    user_info = get_user()
    # set parameter for template
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    if request.session['Error']:
        parameter['error'] = request.session['Error']
        request.session['Error'] = ''
    return render(request, 'link/index.html', parameter)

@login_required
def create_local(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = get_user()
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
            user_info['are_linked'] = True
            user_info['email'] = user_info['mail']
            user_info['o365Email'] = user_info['mail']
            login(user_info)
            return HttpResponseRedirect('/')
    # GET /link/createlocal
    else:
        return render(request, 'link/createlocal.html', parameter)

@login_required
def login_local(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = get_user()
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
                    user_info['are_linked'] = True
                    user_info['email'] = email
                    user_info['o365Email'] = user_info['mail']
                    login(user_info)
                    return HttpResponseRedirect('/')
            errors.append('Invalid login attempt.')
            parameter['errors'] = errors
            return render(request, 'link/loginlocal.html', parameter)
    # GET /link/loginlocal
    else:
        if user_info['local_existed']:
            data = {'Email': user_info['mail']}
            LOCAL_USER.link(user_info, data)
            user_info['are_linked'] = True
            user_info['email'] = user_info['mail']
            user_info['o365Email'] = user_info['mail']
            login(user_info)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'link/loginlocal.html', parameter)

def login_o365(request):
    scheme = request.scheme
    host = request.get_host()
    redirect_uri = '%s://%s/link/ProcessCode' % (scheme, host)
    auth_url = constant.o365_login_url + redirect_uri
    return HttpResponseRedirect(auth_url)

def process_code(request):
    scheme = request.scheme
    host = request.get_host()
    redirect_uri = '%s://%s/link/ProcessCode' % (scheme, host)
    code = request.GET.get('code', '')

    aad_auth_result = TOKEN_SERVICE.get_token_with_code(code, redirect_uri, constant.Resources.AADGraph)
    o365_user_id = aad_auth_result.get('oid')    
    organzation_id = '64446b5c-6d85-4d16-9ff2-94eddc0c2439'
    aad_token = TOKEN_SERVICE.cache_tokens(aad_auth_result, o365_user_id)
    ms_token = TOKEN_SERVICE.get_access_token(constant.Resources.MSGraph, o365_user_id)

    ms_graph_service = MSGraphService(access_token=ms_token)
    graph_user = ms_graph_service.get_me()
    graph_org = ms_graph_service.get_organization(organzation_id)
    
    aad_graph_service = AADGraphService(graph_org['id'], aad_token)
    admin_ids = aad_graph_service.get_admin_ids()
    license_ids = aad_graph_service.get_license_ids()

    o365_user_service = O365UserService()
    user_info = o365_user_service.get_client_user(graph_user, graph_org, admin_ids, license_ids)

    LOCAL_USER.create_organization(user_info)
    LOCAL_USER.check_link_status(user_info)

    if not user_info.get('are_linked', False):
        user = get_user()
        ret = LOCAL_USER.link_o365(user, user_info)
        if ret:
            user_info['are_linked'] = True
            user_info['is_local'] = request.user['is_local']
            user_info['mail'] = request.user['mail']
            login(user_info)
            return HttpResponseRedirect('/')

    request.session['Error'] = 'Failed to link accounts. The Office 365 account %s is already linked to another local account.' % user_info['mail']
    return HttpResponseRedirect('/link')


