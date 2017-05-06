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
from services.auth_service import AuthService
from services.ms_graph_service import MSGraphService
from services.user_service import UserService
from services.link_service import LinkService

from .forms import CreateLocalInfo, LoginLocalInfo

token_service = TokenService()
user_service = UserService()
link_service = LinkService()

@login_required
def link(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user = AuthService.get_current_user(request)
  
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user
    if not user.are_linked and user.is_o365:
        local_user = user_service.get_user_by_o365_email(user.o365_email)
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
    user = AuthService.get_current_user(request)
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
            local_user = user_service.create(user.o365_user)  
        except Exception as e:
            errors.append('Name %s is already taken.' % user.o365_email)
            errors.append("Email '%s' is already taken." % user.o365_email)
            parameter['errors'] = errors
            return render(request, 'link/createlocal.html', parameter)        
        link_service.link(local_user, user.o365_user)
        user_service.update_favorite_color(data['FavoriteColor'], user.user_id)
        auth_login(request, local_user)
        return HttpResponseRedirect('/')
    # GET /link/createlocal
    else:
        return render(request, 'link/createlocal.html', parameter)

@login_required
def login_local(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user = AuthService.get_current_user(request)
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
                link_service.link(local_user, user.o365_user, None)
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
        #     user_service.link(user_info, data)
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
        'nonce': AuthService.get_random_string(),
        'prompt': 'login'
    }
    o365_login_url = AuthService.get_authorization_url(request, 'code+id_token', 'link/ProcessCode', AuthService.get_random_string(), extra_params) 
    return HttpResponseRedirect(o365_login_url)

def process_code(request):    
    AuthService.validate_state(request)
    code = request.POST.get('code')
    id_token = AuthService.get_id_token(request)
    
    o365_user_id = id_token.get('oid')
    tenant_id = id_token.get('tid')

    if link_service.is_linked(o365_user_id):
        request.session['Error'] = 'Failed to link accounts. The Office 365 account %s is already linked to another local account.' % id_token.get('email')
        return HttpResponseRedirect('/link')

    redirect_uri = AuthService.get_redirect_uri(request, 'Auth/O365/Callback')
    auth_result = token_service.get_token_with_code(code, redirect_uri, constant.Resources.MSGraph)
    token_service.cache_tokens(auth_result, o365_user_id) 
    
    ms_graph_service = MSGraphService(auth_result.get('accessToken'))
    o365_user = ms_graph_service.get_o365_user(tenant_id)  
    AuthService.set_o365_user(reqeust, o365_user)

    user = AuthService.get_current_user(request)
    link_service.link(user.local_user, o365_user, None)
 
    response =  HttpResponseRedirect('/')
    response.set_cookie(constant.o365_username_cookie, o365_user.display_name)
    response.set_cookie(constant.o365_email_cookie, o365_user.email)
    return response



