'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth import authenticate as auth_authenticate

from django.conf import settings

import constant
from decorator import login_required
from services.token_service import TokenService
from services.ms_graph_service import MSGraphService
from services.aad_graph_service import AADGraphService
from services.local_user_service import LocalUserService
from services.o365_user_service import O365UserService
from services.auth_service import login, authenticate, logout

from .forms import UserInfo, UserRegInfo

LOCAL_USER = LocalUserService()
TOKEN_SERVICE = TokenService()

def index(request):
    request.session[constant.username_cookie] = ''
    request.session[constant.email_cookie] = ''
    return HttpResponseRedirect('/Account/Login')

def relogin(request):
    login(request)
    request.session[constant.username_cookie] = ''
    request.session[constant.email_cookie] = ''
    user_form = UserInfo()
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    return render(request, 'account/login.html', {'user_form':user_form, 'links':links})

def my_login(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    redirect_scheme = request.scheme
    redirect_host = request.get_host()
    if request.session.get(constant.username_cookie) and request.session.get(constant.email_cookie):
        return HttpResponseRedirect('/Account/O365login')
    # post /Account/Login
    if request.method == 'POST':
        email = ''
        password = ''
        errors = []
        user_form = UserInfo(request.POST)
        if user_form.is_valid():
            data = user_form.clean()
            email = data['Email']
            password = data['Password']
        if email and password:
            user = auth_authenticate(username=email, password=password)
            if user is not None:
                if hasattr(user, 'localuser') and user.localuser.o365UserId:
                    login_local_user(request, user)
                else:
                    user_info = set_local_user(user)
                    login(request, user_info)
            else:
                errors.append('Invalid login attempt.')
                return render(request, 'account/login.html', {'user_form':user_form, 'errors':errors, 'links':links})
            ret = authenticate(request.user)
            if ret:
                if request.user['arelinked']:
                    if request.user['role'] != 'Admin':
                        return HttpResponseRedirect('/Schools')
                    else:
                        return HttpResponseRedirect('/Admin')
                else:
                    return HttpResponseRedirect('/link')
        else:
            if request.session.get(constant.username_cookie) and request.session.get(constant.email_cookie):
                return HttpResponseRedirect('/Account/O365login')
            else:
                redirect_url = constant.o365_signin_url % (redirect_scheme, redirect_host)
                return HttpResponseRedirect(redirect_url)
    # get /Account/Login
    else:
        user_form = UserInfo()
        return render(request, 'account/login.html', {'user_form':user_form, 'links':links})

def set_local_user(user):
    user_info = {}
    user_info['islocal'] = True
    user_info['mail'] = user.email
    user_info['display_name'] = user.username
    user_info['isauthenticated'] = True
    user_info['arelinked'] = False
    return user_info

def login_local_user(request, user):
    aad_token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user.localuser.o365UserId)
    ms_token = TOKEN_SERVICE.get_access_token(constant.Resources.MSGraph, user.localuser.o365UserId)

    ms_graph_service = MSGraphService(token=ms_token)
    ms_client = ms_graph_service.get_client()

    o365_user_service = O365UserService()
    client_user = o365_user_service.get_client_user(ms_client)

    aad_graph_service = AADGraphService(client_user['tenant_id'], aad_token)
    admin_ids = aad_graph_service.get_admin_ids()
    extra_user = aad_graph_service.get_user_extra_info()
    user_info = o365_user_service.get_user(client_user, admin_ids, extra_user)

    LOCAL_USER.check_link_status(user_info)
    login(request, user_info)

    request.session[constant.username_cookie] = user_info['display_name']
    request.session[constant.email_cookie] = user_info['mail']

def o365_auth_callback(request):
    redirect_scheme = request.scheme
    redirect_host = request.get_host()
    redirect_uri = constant.redirect_uri % (redirect_scheme, redirect_host)
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
    LOCAL_USER.check_link_status(user_info)

    login(request, user_info)
    request.session[constant.username_cookie] = user_info['display_name']
    request.session[constant.email_cookie] = user_info['mail']

    if user_info['arelinked']:
        if user_info['role'] != 'Admin':
            return HttpResponseRedirect('/Schools')
        else:
            return HttpResponseRedirect('/Admin')
    else:
        return HttpResponseRedirect('/link')

@login_required
def photo(request, user_object_id):
    token = TOKEN_SERVICE.get_access_token(constant.Resources.MSGraph, request.user['uid'])
    ms_graph_service = MSGraphService(token=token)
    user_photo = ms_graph_service.get_photo(user_object_id)
    if not user_photo:
        local_photo_path = settings.STATICFILES_DIRS[0] + '/Images/DefaultUserPhoto.jpg'
        local_photo_file = open(local_photo_path, 'rb')
        user_photo = local_photo_file.read()
    return HttpResponse(user_photo, content_type='image/jpeg')

def o365_signin(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    username = request.session[constant.username_cookie]
    email = request.session[constant.email_cookie]

    ret = authenticate(request.user)
    if ret:
        token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, request.user['uid'])
        if token:
            return HttpResponseRedirect('/Schools')

    parameter = {}
    parameter['links'] = links
    parameter['username'] = username
    parameter['email'] = email
    return render(request, 'account/O365login.html', parameter)

def external_login(request):
    redirect_scheme = request.scheme
    redirect_host = request.get_host()

    ret = authenticate(request.user)
    if ret:
        aad_token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, request.user['uid'])
        ms_token = TOKEN_SERVICE.get_access_token(constant.Resources.MSGraph, request.user['uid'])
        if aad_token and ms_token:
            return HttpResponseRedirect('/Schools')

    redirect_url = constant.o365_signin_url % (redirect_scheme, redirect_host)
    return HttpResponseRedirect(redirect_url)

def register(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_reg_form = UserRegInfo()
    email = ''
    password = ''
    favoritecolor = ''
    # post /Account/Register
    if request.method == 'POST':
        errors = []
        user_reg_form = UserRegInfo(request.POST)
        if user_reg_form.is_valid():
            data = user_reg_form.clean()
            ret = LOCAL_USER.register(data)
            if ret:
                user_info = {}
                user_info['islocal'] = True
                user_info['isauthenticated'] = True
                user_info['mail'] = data['Email']
                user_info['display_name'] = data['Email']
                user_info['arelinked'] = False
                user_info['uid'] = 'register'
                user_info['tenant_id'] = 'register'
                login(request, user_info)
                return HttpResponseRedirect('/link')
            else:
                errors.append('Name %s is already taken.' % data['Email'])
                errors.append("Email '%s' is already taken." % data['Email'])
                return render(request, 'account/register.html', {'user_reg_form':user_reg_form, 'errors':errors, 'links':links})
    # get /Account/Register
    else:
        return render(request, 'account/register.html', {'user_reg_form':user_reg_form, 'links':links})

@login_required
def logoff(request):
    user_info = request.user
    logout(request)
    if user_info['arelinked']:
        return HttpResponseRedirect('/Account/O365login')
    else:
        request.session[constant.username_cookie] = ''
        request.session[constant.email_cookie] = ''
        redirect_scheme = request.scheme
        redirect_host = request.get_host()
        redirect_uri = redirect_scheme + '://' + redirect_host + '/Account/Login'
        logoff_url = constant.log_out_url % (redirect_uri, redirect_uri)
        return HttpResponseRedirect(logoff_url)

