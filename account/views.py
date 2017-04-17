from django.shortcuts import render, reverse

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.conf import settings

import constant
from decorator import ms_login_required
from .forms import UserInfo, UserRegInfo
from .controller import LocalUserManager, O365UserManager

LOCAL_USER = LocalUserManager()
O365_USER = O365UserManager()

def index(request):
    request.session['ms_user'] = {}
    request.session['aad_token'] = ''
    request.session['aad_refresh'] = ''
    request.session['aad_expires'] = ''
    request.session['ms_token'] = ''
    request.session['ms_refresh'] = ''
    request.session['ms_expires'] = ''
    request.session[constant.username_cookie] = ''
    request.session[constant.email_cookie] = ''
    return HttpResponseRedirect('/Account/Login')

def relogin(request):
    user_form = UserInfo()
    return render(request, 'account/login.html', {'user_form':user_form})

def my_login(request):
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
                login(request, user)
                aad = authenticate(token=request.aad_token, resource='aad')
                ms = authenticate(token=request.ms_token, resource='ms')
                if aad.access_token and ms.access_token:
                    return HttpResponseRedirect('/link')
            else:
                errors.append('Invalid login attempt.')
                return render(request, 'account/login.html', {'user_form':user_form, 'errors':errors})
        # 0365 login
        return HttpResponseRedirect(constant.o365_signin_url)
    # get /Account/Login
    else:
        user_form = UserInfo()
        return render(request, 'account/login.html', {'user_form':user_form})

def merge_o365_user(aad, ms):
    # get admin ids from aad graph api because of ms graph lost directoryRoles members api
    admin_ids = settings.AAD_REQUEST.get_admin_ids(aad.access_token)
    # get assigned_licenses skuIDs from aad graph api because of ms graph lost assigned licenses api
    extra_info = settings.AAD_REQUEST.get_user_extra_info(aad.access_token)
    # get ms client
    ms_client = settings.MS_REQUEST.get_client(ms.access_token)
    # process user info for display
    user_info = O365_USER.normalize_base_user_info(ms_client, extra_info, admin_ids)
    return user_info

def ms_login(request):
    code = request.GET.get('code', '')
    aad = authenticate(code=code, resource='aad')
    ms = authenticate(code=code, resource='ms')
    user_info = merge_o365_user(aad, ms)
    # check user link status
    LOCAL_USER.check_link_status(user_info)

    request.session['ms_user'] = user_info
    request.session['aad_token'] = aad.access_token
    request.session['aad_refresh'] = aad.refresh_token
    request.session['aad_expires'] = aad.expires_on
    request.session['ms_token'] = ms.access_token
    request.session['ms_refresh'] = ms.refresh_token
    request.session['ms_expires'] = ms.expires_on
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
    ms = authenticate(access_token=request.session['ms_token'], refresh_token=request.session['ms_refresh'], expires=request.session['ms_expires'], token_resource='ms', resource='ms')
    # get user photo from ms graph api
    user_photo = settings.MS_REQUEST.get_user_photo(ms.access_token, user_object_id)
    user_photo = ''
    if not user_photo:
        local_photo_path = settings.STATICFILES_DIRS[0] + '/Images/DefaultUserPhoto.jpg'
        local_photo_file = open(local_photo_path, 'rb')
        user_photo = local_photo_file.read()
    return HttpResponse(user_photo, content_type='image/jpeg')

def o365_signin(request):
    username = request.session[constant.username_cookie]
    email = request.session[constant.email_cookie]
    parameter = {}
    parameter['username'] = username
    parameter['email'] = email
    return render(request, 'account/O365login.html', parameter)

def external_login(request):
    return HttpResponseRedirect(constant.o365_signin_url)

def register(request):
    user_reg_form = UserRegInfo()
    email = ''
    password = ''
    favoritecolor = ''
    if request.method == 'POST':
        user_reg_form = UserRegInfo(request.POST)
        if user_reg_form.is_valid():
            data = user_reg_form.clean()
            ret = LOCAL_USER.register(data)
            if ret:
                return HttpResponseRedirect('/')
    return render(request, 'account/register.html', {'user_reg_form':user_reg_form})

