from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate

from .forms import CreateLocalInfo

from decorator import ms_login_required
from account.controller import LocalUserManager

LOCAL_USER = LocalUserManager()

@ms_login_required
def link(request):
    user_info = request.session['ms_user']
    # set parameter for template
    parameter = {}
    parameter['user'] = user_info
    if user_info['arelinked']:
        return HttpResponseRedirect('/Schools')
    else:
        return render(request, 'link/index.html', parameter)

@ms_login_required
def createlocal(request):
    user_info = request.session['ms_user']
    create_local_form = CreateLocalInfo()
    parameter = {}
    parameter['user'] = user_info
    parameter['create_local_form'] = create_local_form
    errors = []
    if request.method == 'POST':
        create_local_form = CreateLocalInfo(request.POST)
        if create_local_form.is_valid():
            data = create_local_form.clean()
            favoritecolor = data['FavoriteColor']
            user_info['color'] = favoritecolor
        ret = LOCAL_USER.create(user_info)
        if not ret:
            errors.append('Name %s is already taken.' % user_info['mail'])
            errors.append("Email '%s' is already taken." % user_info['mail'])
            parameter['errors'] = errors
            return render(request, 'link/createlocal.html', parameter)
        else:
            user_info['arelinked'] = True
            user_info['islocal'] = True
            # restore user info to session for pages
            request.session['ms_user'] = user_info
            return HttpResponseRedirect('/Schools')
    else:
        return render(request, 'link/createlocal.html', parameter)

def loginlocal(request):
    aad = authenticate(access_token=request.session['aad_token'], refresh_token=request.session['aad_refresh'], expires=request.session['aad_expires'], token_resource='aad', resource='aad')
    ms = authenticate(access_token=request.session['ms_token'], refresh_token=request.session['ms_refresh'], expires=request.session['ms_expires'], token_resource='ms', resource='ms')
    user_info = request.session['ms_user']
    LOCAL_USER.link(user_info)
    LOCAL_USER.update_token(user_info['uid'], (aad.access_token, aad.refresh_token, 'aad'))
    LOCAL_USER.update_token(user_info['uid'], (aad.access_token, aad.refresh_token, 'ms'))
    LOCAL_USER.update_role(user_info['uid'], user_info['role'])
    user_info['arelinked'] = True
    user_info['email'] = user_info['mail']
    user_info['o365Email'] = user_info['mail']
    request.session['ms_user'] = user_info
    return HttpResponseRedirect('/Schools')
