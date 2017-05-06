'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
import constant
from utils.shortcuts import render
from decorator import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate as auth_authenticate
from django.conf import settings

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
    user = AuthService.get_current_user(request)
    context = {'user': user}
    if not user.are_linked and user.is_o365:
        local_user = user_service.get_user_by_o365_email(user.o365_email)
        if local_user:
            context['local_existed'] = True
            context['local_message'] = 'There is a local account: %s matching your O365 account.' % user.o365_email
        else:
            context['local_existed'] = False
    if request.session['Error']:
        context['error'] = request.session['Error']
        request.session['Error'] = ''
    return render(request, 'link/index.html', context)

@login_required
def create_local(request):
    user = AuthService.get_current_user(request)
    create_local_form = CreateLocalInfo()
    context = {
        'user': user,
        'create_local_form': create_local_form
    }
    errors = []
    # POST /link/createlocal
    if request.method == 'POST':
        create_local_form = CreateLocalInfo(request.POST)
        data = ''
        if create_local_form.is_valid():
            data = create_local_form.clean()
        try:
            local_user = user_service.create(user.o365_user)
        except:
            errors.append('Name %s is already taken.' % user.o365_email)
            errors.append("Email '%s' is already taken." % user.o365_email)
            context['errors'] = errors
            return render(request, 'link/createlocal.html', context)
        link_service.link(local_user, user.o365_user)
        user_service.update_favorite_color(data['FavoriteColor'], local_user.id)
        local_user = user_service.get_user(local_user.id) # reload local user
        auth_login(request, local_user)
        return HttpResponseRedirect('/')
    # GET /link/createlocal
    else:
        return render(request, 'link/createlocal.html', context)

@login_required
def login_local(request):
    user = AuthService.get_current_user(request)
    login_local_form = LoginLocalInfo()
    context = {
        'user': user,
        'login_local_form': login_local_form
    }
    # POST /link/loginlocal
    if request.method == 'POST':
        login_local_form = LoginLocalInfo(request.POST)
        if login_local_form.is_valid():
            data = login_local_form.clean()
            email = data['Email']
            password = data['Password']
            local_user = auth_authenticate(username=email, password=password)
            if local_user:
                link_service.link(local_user, user.o365_user, None)
                auth_login(request, local_user)
                return HttpResponseRedirect('/')
            else:
                context['errors'] = ['Invalid login attempt.']
            return render(request, 'link/loginlocal.html', context)
    # GET /link/loginlocal
    else:
        return render(request, 'link/loginlocal.html', context)

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

    redirect_uri = AuthService.get_redirect_uri(request, 'link/ProcessCode')
    auth_result = token_service.get_token_with_code(code, redirect_uri, constant.Resources.MSGraph)
    token_service.cache_tokens(auth_result, o365_user_id)

    ms_graph_service = MSGraphService(auth_result.get('accessToken'))
    o365_user = ms_graph_service.get_o365_user(tenant_id)
    AuthService.set_o365_user(request, o365_user)

    user = AuthService.get_current_user(request)
    link_service.link(user.local_user, o365_user)

    response =  HttpResponseRedirect('/')
    response.set_cookie(constant.o365_username_cookie, o365_user.display_name)
    response.set_cookie(constant.o365_email_cookie, o365_user.email)
    return response



