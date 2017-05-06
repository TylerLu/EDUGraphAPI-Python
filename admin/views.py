'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings


import constant
from decorator import admin_only, login_required
from services.auth_service import get_current_user, get_authorization_url, get_random_string, validate_state, get_id_token, get_redirect_uri, get_current_user
from services.token_service import TokenService
from services.aad_graph_service import AADGraphService
from services.local_user_service import LocalUserService

LOCAL_USER = LocalUserService()
TOKEN_SERVICE = TokenService()

@login_required
@admin_only
def admin(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user = get_current_user(request)
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user
    parameter['is_admin_consented'] = LOCAL_USER.is_tenant_consented(user.tenant_id)
    if request.session['Message']:
        parameter['message'] = request.session['Message'].split('\r\n')
        request.session['Message'] = ''
    return render(request, 'admin/index.html', parameter)

@login_required
@admin_only
def linked_accounts(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user = get_current_user(request)
    user_links = LOCAL_USER.get_linked_accounts(user.tenant_id)
    parameter = {}
    parameter['user_links'] = user_links
    parameter['links'] = links
    return render(request, 'admin/linkaccounts.html', parameter)

@login_required
@admin_only
def unlink_account(request, link_id):
    if request.method == 'POST':
        LOCAL_USER.remove_link(link_id)
        return HttpResponseRedirect('/Admin/LinkedAccounts')
    else:
        links = settings.DEMO_HELPER.get_links(request.get_full_path())
        user = get_current_user(request)
        parameter = {}
        parameter['links'] = links

        email, o365Email = LOCAL_USER.get_link(link_id)
        parameter['email'] = email
        parameter['o365Email'] = o365Email
        return render(request, 'admin/unlinkaccounts.html', parameter)

def consent(request):    
    user = get_current_user(request)
    extra_params = {
        'scope': 'openid+profile',
        'nonce': get_random_string(),
        'prompt': 'admin_consent'
    }
    if user.o365_user:
        extra_params['login_hint'] = user.o365_email    
    o365_login_url = get_authorization_url(request, 'code+id_token', 'Admin/ProcessCode', get_random_string(), extra_params) 
    return HttpResponseRedirect(o365_login_url)

def process_code(request):
    validate_state(request)
    id_token = get_id_token(request)    
    tenant_id = id_token.get('tid')

    LOCAL_USER.update_organization(tenant_id, True)
    message = 'Admin consented successfully!'

    user = get_current_user(request)
    if user.is_authenticated:
        request.session['Message'] = message
        return HttpResponseRedirect('/Admin')
    else:
        return HttpResponseRedirect('/Admin/Consent?consented=true')

@login_required
@admin_only
def unconsent(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user = get_current_user(request)
    
    token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user.o365_user_id)
    aad_graph_service = AADGraphService(user.tenant_id, token)
    app_id = aad_graph_service.get_app_id()
    aad_graph_service.delete_app(app_id)
    
    LOCAL_USER.update_organization(user.tenant_id, False)
    LOCAL_USER.remove_links(user.tenant_id)

    request.session['Message'] = 'Admin unconsented successfully!'
    return HttpResponseRedirect('/Admin')

def add_app_roles(request):
    user = get_current_user(request)
    token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user.o365_user_id)
    aad_graph_service = AADGraphService(user.tenant_id, token)
    app_id = aad_graph_service.get_app_id()
    app_name = aad_graph_service.get_app_name()

    if not app_id:
        request.session['Error'] = 'Could not found the service principal. Please provdie the admin consent.'
        return HttpResponseRedirect('/Admin')
    
    aad_graph_service.add_app_users(app_id, app_name)
    count = 0
    request.session["Message"] = 'User access was successfully enabled for %d user(s).' % count if count > 0 else 'User access was enabled for all users.'
    return HttpResponseRedirect("/Admin")

def consent_alone(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    parameter = {}
    parameter['links'] = links
    if request.GET.get('consented') == 'true':
        parameter['consented'] = True
    return render(request, 'admin/consent.html', parameter)


