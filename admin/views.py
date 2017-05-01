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
from services.local_user_service import LocalUserService

LOCAL_USER = LocalUserService()

@login_required
@admin_only
def admin(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.user
    LOCAL_USER.check_admin(user_info)
    login(request, user_info)
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
    return render(request, 'admin/linkedaccounts.html', parameter)

@login_required
@admin_only
def unlink_account(request, link_id):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.user
    LOCAL_USER.remove_link(link_id)
    user_links = LOCAL_USER.get_links(user_info['tenant_id'])
    parameter = {}
    parameter['user'] = user_info
    parameter['user_links'] = user_links
    parameter['links'] = links
    return render(request, 'admin/linkedaccounts.html', parameter)

@login_required
@admin_only
def consent(request):
    user_info = request.user
    LOCAL_USER.update_organization(user_info, True)
    redirect_scheme = request.scheme
    redirect_host = request.get_host()
    redirect_url = constant.admin_consent_url % (redirect_scheme, redirect_host)
    return HttpResponseRedirect(redirect_url)

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

def only_consent(request):
    redirect_scheme = request.scheme
    redirect_host = request.get_host()
    redirect_url = constant.admin_consent_url % (redirect_scheme, redirect_host)
    return HttpResponseRedirect(redirect_url)

def consent_alone(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.user
    user_info['isauthenticated'] = False
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['consented'] = True
    return render(request, 'admin/consent.html', parameter)
