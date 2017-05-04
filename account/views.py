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
from services.auth_service import authenticate, get_user, logout

from .forms import UserInfo, UserRegInfo

LOCAL_USER = LocalUserService()
TOKEN_SERVICE = TokenService()

def index(request):
    request.session['Error'] = ''
    request.session['Message'] = ''
    user = get_user()
    if not authenticate(user):
        response =  HttpResponseRedirect('/Account/Login')
        response.set_cookie(constant.username_cookie, '')
        response.set_cookie(constant.email_cookie, '')
        return response
    else:
        if not user['are_linked']:
            return HttpResponseRedirect('/link')
        else:
            if user['role'] == 'Admin':
                return HttpResponseRedirect('/Admin')
            else:
                return HttpResponseRedirect('/Schools')

def relogin(request):
    logout()
    user_form = UserInfo()
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    response = render(request, 'account/login.html', {'user_form':user_form, 'links':links})
    response.set_cookie(constant.username_cookie, '')
    response.set_cookie(constant.email_cookie, '')
    return response

def login(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    parameter = {}
    parameter['links'] = links
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
                parameter['user_form'] = user_form
                parameter['errors'] = errors
                return render(request, 'account/login.html', parameter)
    # get /Account/Login
    else:
        user_form = UserInfo()
        parameter['user_form'] = user_form
        return render(request, 'account/login.html', parameter)

def o365_login(request):
    username = request.COOKIES.get(constant.username_cookie)
    email = request.COOKIES.get(constant.email_cookie)
    if username and email:
        links = settings.DEMO_HELPER.get_links(request.get_full_path())
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

    auth_login(user_info)
    response =  HttpResponseRedirect('/')
    response.set_cookie(constant.username_cookie, user_info['display_name'])
    response.set_cookie(constant.email_cookie, user_info['mail'])
    return response

def o365_signin(request):
    scheme = request.scheme
    host = request.get_host()
    redirect_uri = '%s://%s/Auth/O365/Callback' % (scheme, host)
    o365_login_url = constant.o365_signin_url + redirect_uri
    return HttpResponseRedirect(o365_login_url)

@login_required
def photo(request, user_object_id):
    user = get_user()
    token = TOKEN_SERVICE.get_access_token(constant.Resources.MSGraph, user['uid'])
    ms_graph_service = MSGraphService(access_token=token)
    user_photo = ms_graph_service.get_photo(user_object_id)
    if not user_photo:
        local_photo_path = settings.STATICFILES_DIRS[0] + '/Images/DefaultUserPhoto.jpg'
        local_photo_file = open(local_photo_path, 'rb')
        user_photo = local_photo_file.read()
    return HttpResponse(user_photo, content_type='image/jpeg')

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
    user_info = get_user()
    logout()
    if user_info['are_linked']:
        return HttpResponseRedirect('/')
    else:
        scheme = request.scheme
        host = request.get_host()
        redirect_uri = scheme + '://' + host
        logoff_url = constant.log_out_url % (redirect_uri, redirect_uri)
        response =  HttpResponseRedirect(logoff_url)
        response.set_cookie(constant.username_cookie, '')
        response.set_cookie(constant.email_cookie, '')
        return response

def login_local_user(request, user):
    if not hasattr(user, 'localuser') or not user.localuser.o365UserId:
        user_info = get_user()
        user_info['is_local'] = True
        user_info['mail'] = user.email
        user_info['display_name'] = user.username
        user_info['is_authenticated'] = True
        user_info['are_linked'] = False
        user_info['uid'] = 'local'
        user_info['tenant_id'] = 'local'
        auth_login(user_info)
    else:
        aad_token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user.localuser.o365UserId)
        ms_token = TOKEN_SERVICE.get_access_token(constant.Resources.MSGraph, user.localuser.o365UserId)

        organzation_id = '64446b5c-6d85-4d16-9ff2-94eddc0c2439'
        ms_graph_service = MSGraphService(access_token=ms_token)
        graph_user = ms_graph_service.get_me()
        graph_org = ms_graph_service.get_organization(organzation_id)

        aad_graph_service = AADGraphService(graph_org['id'], aad_token)
        admin_ids = aad_graph_service.get_admin_ids()
        license_ids = aad_graph_service.get_license_ids()

        o365_user_service = O365UserService()
        user_info = o365_user_service.get_client_user(graph_user, graph_org, admin_ids, license_ids)

        LOCAL_USER.check_link_status(user_info)
        auth_login(user_info)

        request.set_cookie(constant.username_cookie, user_info['display_name'])
        request.set_cookie(constant.email_cookie, user_info['mail'])
