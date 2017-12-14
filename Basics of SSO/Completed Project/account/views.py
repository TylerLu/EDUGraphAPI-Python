'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import constant
from utils.shortcuts import render

from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate as auth_authenticate
from django.http import HttpResponse, HttpResponseRedirect

from decorator import login_required
from services.token_service import TokenService
from services.ms_graph_service import MSGraphService
from services.user_service import UserService
from services.auth_service import AuthService
from .forms import UserInfo, UserRegInfo

user_service = UserService()
token_service = TokenService()


def index(request):
    user = AuthService.get_current_user(request)
    if not user.is_authenticated:
        return HttpResponseRedirect('/Account/Login')
    else:
        return HttpResponseRedirect('/Schools')

def login(request):
    # get /Account/Login
    if request.method == 'GET':
       user_form = UserInfo()
       return render(request, 'account/login.html', { 'user_form': user_form })   
    # post /Account/Login
    else:        
        return login_post(request)
        
def login_post(request):
    email = ''
    password = ''
    errors = []
    user_form = UserInfo(request.POST)
    if user_form.is_valid():
        data = user_form.clean()
        email = data['Email']
        password = data['Password']
        rememberme = data['RememberMe']
        settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = not rememberme
        user = auth_authenticate(username=email, password=password)
        if user is not None:
            auth_login(request, user)
            o365_user = user_service.get_o365_user(user)
            if o365_user:
                AuthService.set_o365_user(request, o365_user)
            return HttpResponseRedirect('/')
    errors.append('Invalid login attempt.')
    context = {
        'user_form': user_form,
        'errors': errors
    }
    return render(request, 'account/login.html', context)

def o365_login(request):
    extra_params = {
        'scope': 'openid+profile',
        'nonce': AuthService.get_random_string()
    }
    o365_email = request.COOKIES.get(constant.o365_email_cookie)
    if o365_email:
        extra_params['login_hint'] = o365_email
    else:
        extra_params['prompt'] = 'login'
    o365_login_url = AuthService.get_authorization_url(request, 'code+id_token', 'Auth/O365/Callback', AuthService.get_random_string(), extra_params)
    settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    return HttpResponseRedirect(o365_login_url)



def o365_auth_callback(request):
    
    AuthService.validate_state(request)
    code = request.POST.get('code')
    id_token = AuthService.get_id_token(request)
    
    o365_user_id = id_token.get('oid')
    tenant_id = id_token.get('tid')

    redirect_uri = AuthService.get_redirect_uri(request, 'Auth/O365/Callback')
    auth_result = token_service.get_token_with_code(code, redirect_uri, constant.Resources.MSGraph)
    token_service.cache_tokens(auth_result, o365_user_id)

    ms_graph_service = MSGraphService(auth_result.get('accessToken'))
    
    o365_user = ms_graph_service.get_o365_user(tenant_id)
    
    AuthService.set_o365_user(request, o365_user)

    local_user = user_service.get_user_by_o365_email(o365_user.email)
    if local_user:
        auth_login(request, local_user)

    response =  HttpResponseRedirect('/')
    response.set_cookie(constant.o365_username_cookie, o365_user.display_name)
    response.set_cookie(constant.o365_email_cookie, o365_user.email)
    return response



def register(request):
    user_reg_form = UserRegInfo()
    # post /Account/Register
    if request.method == 'POST':
        errors = []
        user_reg_form = UserRegInfo(request.POST)
        if user_reg_form.is_valid():
            data = user_reg_form.clean()
            user = user_service.register(data['Email'], data['Password'],'')
            if user:
                auth_login(request, user)
                return HttpResponseRedirect('/')
            else:
                errors.append('Name %s is already taken.' % data['Email'])
                errors.append("Email '%s' is already taken." % data['Email'])
                return render(request, 'account/register.html', {'user_reg_form':user_reg_form, 'errors':errors})
    # get /Account/Register
    else:
        return render(request, 'account/register.html', {'user_reg_form':user_reg_form})

@login_required
def logoff(request):
    user = AuthService.get_current_user(request)
    AuthService.clear_o365_user(request)
    auth_logout(request)
    return HttpResponseRedirect('/')