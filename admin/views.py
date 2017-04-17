from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from decorator import ms_login_required

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

def linkaccounts(request):
    # get user info from session
    user_info = request.session['ms_user']
    links = LOCAL_USER.get_links()
    parameter = {}
    parameter['user'] = user_info
    parameter['links'] = links
    return render(request, 'admin/linkedaccounts.html', parameter)

def unlinkaccounts(request, link_id):
    # get user info from session
    user_info = request.session['ms_user']
    LOCAL_USER.remove_link(link_id)
    links = LOCAL_USER.get_links()
    parameter = {}
    parameter['user'] = user_info
    parameter['links'] = links
    return render(request, 'admin/linkedaccounts.html', parameter)

def consent(request):
    return HttpResponseRedirect(constant.admin_consent_url)

def unconsent(request):
    # get user info from session
    user_info = request.session['ms_user']
    user_info['isadminconsented'] = False
    parameter = {}
    parameter['user'] = user_info
    return render(request, 'admin/index.html', parameter)
