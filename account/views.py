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
from services.auth_service import login as auth_login 
from services.auth_service import authenticate, logout

from .forms import UserInfo, UserRegInfo

LOCAL_USER = LocalUserService()
TOKEN_SERVICE = TokenService()

def index(request):
    if not authenticate(request.user):
        response =  HttpResponseRedirect('/Account/Login')
        response.set_cookie(constant.username_cookie, '')
        response.set_cookie(constant.email_cookie, '')
        return response
    else:
        if not request.user['are_linked']:
            return HttpResponseRedirect('/link')
        else:
            if request.user['role'] == 'Admin':
                return HttpResponseRedirect('/Admin')
            else:
                return HttpResponseRedirect('/Schools')

def relogin(request):
    auth_login(request)
    user_form = UserInfo()
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    response = render(request, 'account/login.html', {'user_form':user_form, 'links':links})
    response.set_cookie(constant.username_cookie, '')
    response.set_cookie(constant.email_cookie, '')
    return response

def login(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
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
                login_local_user(request, user)
                return HttpResponseRedirect('/')
            else:
                errors.append('Invalid login attempt.')
                return render(request, 'account/login.html', {'user_form':user_form, 'errors':errors, 'links':links})
    # get /Account/Login
    else:
        user_form = UserInfo()
        return render(request, 'account/login.html', {'user_form':user_form, 'links':links})

def o365_login(request):
    if request.COOKIES.get(constant.username_cookie) and request.COOKIES.get(constant.email_cookie):
        links = settings.DEMO_HELPER.get_links(request.get_full_path())
        username = request.COOKIES[constant.username_cookie]
        email = request.COOKIES[constant.email_cookie]
        parameter = {}
        parameter['links'] = links
        parameter['username'] = username
        parameter['email'] = email
        return render(request, 'account/O365login.html', parameter)
    else:
        scheme = request.scheme
        host = request.get_host()
        redirect_uri = '%s://%s/Auth/O365/Callback' % (scheme, host)
        o365_login_url = constant.o365_login_url + redirect_uri
        return HttpResponseRedirect(o365_login_url)

def o365_auth_callback(request):
    scheme = request.scheme
    host = request.get_host()
    redirect_uri = '%s://%s/Auth/O365/Callback' % (scheme, host)
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

    auth_login(request, user_info)
    response =  HttpResponseRedirect('/')
    response.set_cookie(constant.username_cookie, user_info['display_name'], 300)
    response.set_cookie(constant.email_cookie, user_info['mail'], 300)
    return response

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

def o365_login_only(request):
    scheme = request.scheme
    host = request.get_host()
    redirect_uri = '%s://%s/Auth/O365/Callback' % (scheme, host)
    o365_login_url = constant.o365_signin_url + redirect_uri
    return HttpResponseRedirect(o365_login_url)

def register(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_reg_form = UserRegInfo()
    # post /Account/Register
    if request.method == 'POST':
        errors = []
        user_reg_form = UserRegInfo(request.POST)
        if user_reg_form.is_valid():
            data = user_reg_form.clean()
            ret = LOCAL_USER.register(data)
            if ret:
                user_info = {}
                user_info['is_local'] = True
                user_info['is_authenticated'] = True
                user_info['mail'] = data['Email']
                user_info['display_name'] = data['Email']
                user_info['are_linked'] = False
                user_info['uid'] = 'register'
                user_info['tenant_id'] = 'register'
                auth_login(request, user_info)
                return HttpResponseRedirect('/')
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
    if user_info['are_linked']:
        return HttpResponseRedirect('/')
    else:
        request.set_cookie(constant.username_cookie, '')
        request.set_cookie(constant.email_cookie, '')
        scheme = request.scheme
        host = request.get_host()
        redirect_uri = scheme + '://' + host
        logoff_url = constant.log_out_url % (redirect_uri, redirect_uri)
        return HttpResponseRedirect(logoff_url)

def login_local_user(request, user):
    if not hasattr(user, 'localuser') or not user.localuser.o365UserId:
        user_info = request.user
        user_info['is_local'] = True
        user_info['mail'] = user.email
        user_info['display_name'] = user.username
        user_info['is_authenticated'] = True
        user_info['are_linked'] = False
        auth_login(request, user_info)
    else:
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
        auth_login(request, user_info)

        request.set_cookie(constant.username_cookie, user_info['display_name'])
        request.set_cookie(constant.email_cookie, user_info['mail'])
