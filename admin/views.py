'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from decorator import ms_login_required

import constant
from services.user_service import LocalUserService

LOCAL_USER = LocalUserService()

@ms_login_required
def admin(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.session['ms_user']
    user_info['isadminconsented'] = True
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    return render(request, 'admin/index.html', parameter)

@ms_login_required
def linkaccounts(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.session['ms_user']
    user_links = LOCAL_USER.get_links()
    parameter = {}
    parameter['user'] = user_info
    parameter['user_links'] = user_links
    parameter['links'] = links
    return render(request, 'admin/linkedaccounts.html', parameter)

@ms_login_required
def unlinkaccounts(request, link_id):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.session['ms_user']
    LOCAL_USER.remove_link(link_id)
    user_links = LOCAL_USER.get_links()
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['user_links'] = user_links
    return render(request, 'admin/linkedaccounts.html', parameter)

#@ms_login_required
def consent(request):
    redirect_scheme = request.scheme
    redirect_host = request.get_host()
    redirect_url = constant.admin_consent_url % (redirect_scheme, redirect_host)
    return HttpResponseRedirect(redirect_url)

def consent_alone(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.session['ms_user']
    user_info['isauthenticated'] = False
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['consented'] = True
    return render(request, 'admin/consent.html', parameter)

@ms_login_required
def unconsent(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.session['ms_user']
    user_info['isadminconsented'] = False
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    return render(request, 'admin/index.html', parameter)
