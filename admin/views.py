from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from decorator import ms_login_required

import constant
from account.controller import LocalUserManager

LOCAL_USER = LocalUserManager()

@ms_login_required
def admin(request):
    # get user info from session
    user_info = request.session['ms_user']
    user_info['isadminconsented'] = True
    parameter = {}
    parameter['user'] = user_info
    return render(request, 'admin/index.html', parameter)

@ms_login_required
def linkaccounts(request):
    # get user info from session
    user_info = request.session['ms_user']
    links = LOCAL_USER.get_links()
    parameter = {}
    parameter['user'] = user_info
    parameter['links'] = links
    return render(request, 'admin/linkedaccounts.html', parameter)

@ms_login_required
def unlinkaccounts(request, link_id):
    # get user info from session
    user_info = request.session['ms_user']
    LOCAL_USER.remove_link(link_id)
    links = LOCAL_USER.get_links()
    parameter = {}
    parameter['user'] = user_info
    parameter['links'] = links
    return render(request, 'admin/linkedaccounts.html', parameter)

@ms_login_required
def consent(request):
    redirect_scheme = request.scheme
    redirect_host = request.get_host()
    redirect_url = constant.admin_consent_url % (redirect_scheme, redirect_host)
    return HttpResponseRedirect(redirect_url)

@ms_login_required
def unconsent(request):
    # get user info from session
    user_info = request.session['ms_user']
    user_info['isadminconsented'] = False
    parameter = {}
    parameter['user'] = user_info
    return render(request, 'admin/index.html', parameter)
