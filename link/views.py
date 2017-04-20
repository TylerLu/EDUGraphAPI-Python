from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.conf import settings

from .forms import CreateLocalInfo, LoginLocalInfo

from decorator import ms_login_required
from account.controller import LocalUserManager

LOCAL_USER = LocalUserManager()

@ms_login_required
def link(request):
    user_info = request.session['ms_user']
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    # set parameter for template
    parameter = {}
    parameter['user'] = user_info
    parameter['links'] = links
    return render(request, 'link/index.html', parameter)

@ms_login_required
def createlocal(request):
    user_info = request.session['ms_user']
    create_local_form = CreateLocalInfo()
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    parameter = {}
    parameter['user'] = user_info
    parameter['create_local_form'] = create_local_form
    parameter['links'] = links
    errors = []
    # POST /link/createlocal
    if request.method == 'POST':
        create_local_form = CreateLocalInfo(request.POST)
        if create_local_form.is_valid():
            data = create_local_form.clean()
            favoritecolor = data['FavoriteColor']
            user_info['color'] = favoritecolor
        aad = authenticate(access_token=request.session['aad_token'], refresh_token=request.session['aad_refresh'], expires=request.session['aad_expires'], resource='aad')
        ms = authenticate(access_token=request.session['ms_token'], refresh_token=request.session['ms_refresh'], expires=request.session['ms_expires'], resource='ms')
        ret = LOCAL_USER.create(user_info)
        LOCAL_USER.update_token(user_info['uid'], (aad.access_token, aad.refresh_token, aad.expires_on, 'aad'))
        LOCAL_USER.update_token(user_info['uid'], (ms.access_token, ms.refresh_token, ms.expires_on, 'ms'))
        LOCAL_USER.update_role(user_info['uid'], user_info['role'])
        if not ret:
            errors.append('Name %s is already taken.' % user_info['mail'])
            errors.append("Email '%s' is already taken." % user_info['mail'])
            parameter['errors'] = errors
            return render(request, 'link/createlocal.html', parameter)
        else:
            user_info['arelinked'] = True
            user_info['email'] = user_info['mail']
            user_info['o365Email'] = user_info['mail']
            request.session['ms_user'] = user_info
            return HttpResponseRedirect('/Schools')
    # GET /link/createlocal
    else:
        return render(request, 'link/createlocal.html', parameter)

@ms_login_required
def loginlocal(request):
    user_info = request.session['ms_user']
    login_local_form = LoginLocalInfo()
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    parameter = {}
    parameter['user'] = user_info
    parameter['login_local_form'] = login_local_form
    parameter['links'] = links
    # POST /link/loginlocal
    if request.method == 'POST':
        login_local_form = LoginLocalInfo(request.POST)
        if login_local_form.is_valid():
            data = login_local_form.clean()
            email = data['Email']
            password = data['Password']
            user = authenticate(username=email, password=password)
            if user is not None:
                aad = authenticate(access_token=request.session['aad_token'], refresh_token=request.session['aad_refresh'], expires=request.session['aad_expires'], resource='aad')
                ms = authenticate(access_token=request.session['ms_token'], refresh_token=request.session['ms_refresh'], expires=request.session['ms_expires'], resource='ms')
                user_info = request.session['ms_user']
                LOCAL_USER.link(user_info, data)
                LOCAL_USER.update_token(user_info['uid'], (aad.access_token, aad.refresh_token, aad.expires_on, 'aad'))
                LOCAL_USER.update_token(user_info['uid'], (ms.access_token, ms.refresh_token, ms.expires_on, 'ms'))
                LOCAL_USER.update_role(user_info['uid'], user_info['role'])
                user_info['arelinked'] = True
                user_info['email'] = email
                user_info['o365Email'] = user_info['mail']
                request.session['ms_user'] = user_info
                return HttpResponseRedirect('/Schools')
    # GET /link/loginlocal
    else:
        return render(request, 'link/loginlocal.html', parameter)
