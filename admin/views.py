'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings


import constant
from decorator import admin_only, login_required
from services.auth_service import login
from services.token_service import TokenService
from services.local_user_service import LocalUserService

LOCAL_USER = LocalUserService()
TOKEN_SERVICE = TokenService()

@login_required
@admin_only
def admin(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.user
    LOCAL_USER.check_admin(user_info)
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    return render(request, 'admin/index.html', parameter)

@login_required
@admin_only
def linked_accounts(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.user
    user_links = LOCAL_USER.get_links(user_info['tenant_id'])
    parameter = {}
    parameter['user'] = user_info
    parameter['user_links'] = user_links
    parameter['links'] = links
    return render(request, 'admin/linkaccounts.html', parameter)

@login_required
@admin_only
def unlink_account(request, link_id):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.user
    parameter = {}
    parameter['user'] = user_info
    parameter['links'] = links
    if request.method == 'POST':
        LOCAL_USER.remove_link(link_id)
        user_links = LOCAL_USER.get_links(user_info['tenant_id'])
        parameter['user_links'] = user_links
        return render(request, 'admin/linkaccounts.html', parameter)
    else:
        return render(request, 'admin/unlinkaccounts.html', parameter)

@login_required
@admin_only
def consent(request):
    user_info = request.user
    LOCAL_USER.update_organization(user_info, True)
    scheme = request.scheme
    host = request.get_host()
    redirect_uri = '%s://%s/Auth/O365/Callback' % (scheme, host)
    consent_url = constant.admin_consent_url + redirect_uri
    return HttpResponseRedirect(consent_url)

@login_required
@admin_only
def unconsent(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.user
    LOCAL_USER.update_organization(user_info, False)
    LOCAL_USER.remove_links(user_info['tenant_id'])
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    return HttpResponseRedirect('/Admin')

def add_app_roles(request):
    return HttpResponseRedirect('/')

def consent_alone(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.user
    user_info['is_authenticated'] = False
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['consented'] = True
    return render(request, 'admin/consent.html', parameter)

def only_consent(request):
    scheme = request.scheme
    host = request.get_host()
    redirect_uri = '%s://%s/Auth/O365/Callback' % (scheme, host)
    consent_url = constant.admin_consent_url + redirect_uri
    return HttpResponseRedirect(consent_url)

