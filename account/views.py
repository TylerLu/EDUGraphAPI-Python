'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth import authenticate, login

from django.conf import settings

import constant
from services.token_service import TokenService
from services.local_user_service import LocalUserService
from services.o365_user_service import O365UserService

from .forms import UserInfo, UserRegInfo

LOCAL_USER = LocalUserService()
O365_USER = O365UserService()
TOKEN_SERVICE = TokenService()

def index(request):
    request.session['ms_user'] = {}
    request.session[constant.username_cookie] = ''
    request.session[constant.email_cookie] = ''
    return HttpResponseRedirect('/Account/Login')

def relogin(request):
    request.session['ms_user'] = {}
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
            user = authenticate(username=email, password=password)
        if user is not None:
            if hasattr(user, 'localuser') and user.localuser.o365Email:
                user_info = LOCAL_USER.get_user(user.username)
                request.session['ms_user'] = user_info
                return HttpResponseRedirect('/link')
            else:
                errors.append('Invalid login attempt.')
                return render(request, 'account/login.html', {'user_form':user_form, 'errors':errors, 'links':links})
        # 0365 login
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

def ms_login(request):
    redirect_scheme = request.scheme
    redirect_host = request.get_host()
    redirect_uri = constant.redirect_uri % (redirect_scheme, redirect_host)
    code = request.GET.get('code', '')
    if code:
        TOKEN_SERVICE.code = code
        TOKEN_SERVICE.redirect_uri = redirect_uri

    token = TOKEN_SERVICE.get_access_token('aad')
    ms_token = TOKEN_SERVICE.get_access_token('ms')
    user_info = O365_USER.get_current_user(token, ms_token)

    LOCAL_USER.check_link_status(user_info)

    request.session['ms_user'] = user_info
    request.session[constant.username_cookie] = user_info['display_name']
    request.session[constant.email_cookie] = user_info['mail']

    if user_info['arelinked']:
        if user_info['role'] != 'Admin':
            return HttpResponseRedirect('/Schools')
        else:
            return HttpResponseRedirect('/Admin')
    else:
        return HttpResponseRedirect('/link')

def photo(request, user_object_id):
    token = TOKEN_SERVICE.get_access_token('ms')
    user_photo = O365_USER.get_photo(token, user_object_id)
    if not user_photo:
        local_photo_path = settings.STATICFILES_DIRS[0] + '/Images/DefaultUserPhoto.jpg'
        local_photo_file = open(local_photo_path, 'rb')
        user_photo = local_photo_file.read()
    return HttpResponse(user_photo, content_type='image/jpeg')

def o365_signin(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    username = request.session[constant.username_cookie]
    email = request.session[constant.email_cookie]

    token = TOKEN_SERVICE.get_access_token('aad')
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
    token = TOKEN_SERVICE.get_access_token('aad')
    ms_token = TOKEN_SERVICE.get_access_token('ms')
    if token and ms_token:
        return HttpResponseRedirect('/Schools')
    else:
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
                user_info['isauthenticated'] = True
                user_info['islocal'] = True
                user_info['display_name'] = data['Email']
                request.session['ms_user'] = user_info
                return HttpResponseRedirect('/link')
            else:
                errors.append('Name %s is already taken.' % data['Email'])
                errors.append("Email '%s' is already taken." % data['Email'])
                return render(request, 'account/register.html', {'user_reg_form':user_reg_form, 'errors':errors, 'links':links})
    # get /Account/Register
    else:
        return render(request, 'account/register.html', {'user_reg_form':user_reg_form, 'links':links})

def login_o365(request):
    redirect_scheme = request.scheme
    redirect_host = request.get_host()
    redirect_url = constant.o365_login_url % (redirect_scheme, redirect_host)
    return HttpResponseRedirect(redirect_url)

def logoff(request):
    request.session['ms_user'] = {}
    request.session[constant.username_cookie] = ''
    request.session[constant.email_cookie] = ''
    redirect_scheme = request.scheme
    redirect_host = request.get_host()
    redirect_uri = redirect_scheme + '://' + redirect_host + '/Account/Login'
    logoff_url = constant.log_out_url % (redirect_uri, redirect_uri)
    return HttpResponseRedirect(logoff_url)
    
