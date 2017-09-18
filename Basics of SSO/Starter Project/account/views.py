'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''


from utils.shortcuts import render
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate as auth_authenticate
from django.http import HttpResponse, HttpResponseRedirect

from decorator import login_required
from services.user_service import UserService
from services.auth_service import AuthService
from .forms import UserInfo, UserRegInfo

user_service = UserService()



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
    auth_logout(request)
    return HttpResponseRedirect('/')
