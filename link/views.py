'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate as auth_authenticate
from django.conf import settings

import constant
from decorator import login_required
from services.token_service import TokenService
from services.auth_service import get_current_user, get_random_string, get_authorization_url, validate_state, get_id_token, get_redirect_uri
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
    user = get_current_user(request)
  
    # set parameter for template
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user
    if not user.are_linked and user.is_o365:
        local_user = LOCAL_USER.get_user_by_o365_email(user.o365_email)
        if local_user:
            parameter['local_existed'] = True
            parameter['local_message'] = 'There is a local account: %s matching your O365 account.' % user.o365_email
        else:
            parameter['local_existed'] = False
    if request.session['Error']:
        parameter['error'] = request.session['Error']
        request.session['Error'] = ''
    return render(request, 'link/index.html', parameter)

@login_required
def create_local(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user = get_current_user(request)
    create_local_form = CreateLocalInfo()
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user
    parameter['create_local_form'] = create_local_form
    errors = []
    # POST /link/createlocal
    if request.method == 'POST':
        create_local_form = CreateLocalInfo(request.POST)
        data = ''
        if create_local_form.is_valid():
            data = create_local_form.clean()
        try:
            local_user = LOCAL_USER.create(user.o365_user)  
        except Exception as e:
            errors.append('Name %s is already taken.' % user.o365_email)
            errors.append("Email '%s' is already taken." % user.o365_email)
            parameter['errors'] = errors
            return render(request, 'link/createlocal.html', parameter)        
        LOCAL_USER.link(local_user, user.o365_user, data['FavoriteColor'])
        auth_login(request, local_user)
        return HttpResponseRedirect('/')
    # GET /link/createlocal
    else:
        return render(request, 'link/createlocal.html', parameter)

@login_required
def login_local(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user = get_current_user(request)
    login_local_form = LoginLocalInfo()
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user
    parameter['login_local_form'] = login_local_form
    errors = []
    # POST /link/loginlocal
    if request.method == 'POST':
        login_local_form = LoginLocalInfo(request.POST)
        if login_local_form.is_valid():
            data = login_local_form.clean()
            email = data['Email']
            password = data['Password']
            local_user = auth_authenticate(username=email, password=password)
            if local_user:
                import pdb; pdb.set_trace()
                LOCAL_USER.link(local_user, user.o365_user, None)
                auth_login(request, local_user)
                return HttpResponseRedirect('/')
            else:
                errors.append('Invalid login attempt.')
                parameter['errors'] = errors
            return render(request, 'link/loginlocal.html', parameter)
    # GET /link/loginlocal
    else:
        # if user_info['local_existed']:
        #     data = {'Email': user_info['mail']}
        #     LOCAL_USER.link(user_info, data)
        #     user_info['are_linked'] = True
        #     user_info['email'] = user_info['mail']
        #     user_info['o365Email'] = user_info['mail']
        #     login(user_info)
        #     return HttpResponseRedirect('/')
        # else:
        return render(request, 'link/loginlocal.html', parameter)

def login_o365(request):
    extra_params = {
        'scope': 'openid+profile',
        'nonce': get_random_string(),
        'prompt': 'login'
    }
    o365_login_url = get_authorization_url(request, 'code+id_token', 'link/ProcessCode', get_random_string(), extra_params) 
    return HttpResponseRedirect(o365_login_url)

def process_code(request):    
    validate_state(request)
    code = request.POST.get('code')
    id_token = get_id_token(request)
    
    o365_user_id = id_token.get('oid')
    tenant_id = id_token.get('tid')

    if LOCAL_USER.is_o365_user_linked(o365_user_id):
        request.session['Error'] = 'Failed to link accounts. The Office 365 account %s is already linked to another local account.' % id_token.get('email')
        return HttpResponseRedirect('/link')

    redirect_uri = get_redirect_uri(request, 'link/ProcessCode')
    aad_auth_result = TOKEN_SERVICE.get_token_with_code(code, redirect_uri, constant.Resources.AADGraph)
    aad_token = TOKEN_SERVICE.cache_tokens(aad_auth_result, o365_user_id)    
    ms_token = TOKEN_SERVICE.get_access_token(constant.Resources.MSGraph, o365_user_id)

    o365_user_service = O365UserService(tenant_id, ms_token, aad_token)
    o365_user = o365_user_service.get_o365_user()    
    request.session[constant.o365_user_session_key] = o365_user.to_json()

    user = get_current_user(request)
    LOCAL_USER.link(user.local_user, o365_user, None)
 
    response =  HttpResponseRedirect('/')
    response.set_cookie(constant.o365_username_cookie, o365_user.display_name)
    response.set_cookie(constant.o365_email_cookie, o365_user.email)
    return response



