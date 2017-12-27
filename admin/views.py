'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import constant
from decorator import admin_only, login_required
from utils.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from services.auth_service import AuthService
from services.token_service import TokenService
from services.aad_graph_service import AADGraphService
from services.user_service import UserService
from services.link_service import LinkService

token_service = TokenService()
user_service = UserService()
link_service = LinkService()

@login_required
@admin_only
def admin(request):
    user = AuthService.get_current_user(request)
    context = {
        'user': user,
        'is_admin_consented': user_service.is_tenant_consented(user.tenant_id)
    }
    return render(request, 'admin/index.html', context)

def consent(request): 
      
    user = AuthService.get_current_user(request)
    extra_params = {
        'scope': 'openid+profile',
        'nonce': AuthService.get_random_string(),
        'prompt': 'admin_consent'
    }
    if user.o365_user:
        extra_params['login_hint'] = user.o365_email    
    o365_login_url = AuthService.get_authorization_url(request, 'code+id_token', 'Admin/ProcessCode', AuthService.get_random_string(), extra_params) 
    return HttpResponseRedirect(o365_login_url)

def consent_alone(request):
    context = {}
    
    if request.GET.get('consented') == 'true':
        context['consented'] = True
    return render(request, 'admin/consent.html', context)

def process_code(request):
    AuthService.validate_state(request)
    id_token = AuthService.get_id_token(request)    
    tenant_id = id_token.get('tid')

    user_service.update_organization(tenant_id, True)
    message = 'Admin consented successfully!'

    user = AuthService.get_current_user(request)
    if user.is_authenticated:
        request.session['Message'] = message
        return HttpResponseRedirect('/Admin')
    else:
        return HttpResponseRedirect('/Admin/Consent?consented=true')

@login_required
@admin_only
def unconsent(request):
    user = AuthService.get_current_user(request)    
    token = token_service.get_access_token(constant.Resources.AADGraph, user.o365_user_id)
    aad_graph_service = AADGraphService(user.tenant_id, token)

    service_principal = aad_graph_service.get_service_principal()
    if service_principal:
        aad_graph_service.delete_service_principal(service_principal['objectId'])    
    user_service.update_organization(user.tenant_id, False)
    link_service.remove_links(user.tenant_id)

    request.session['Message'] = 'Admin unconsented successfully!'
    return HttpResponseRedirect('/Admin')

@login_required
@admin_only
def linked_accounts(request):
    user = AuthService.get_current_user(request)
    account_links = link_service.get_links(user.tenant_id)
    context = {
        'user': user,
        'account_links': account_links
    }
    return render(request, 'admin/linkedaccounts.html', context)

@login_required
@admin_only
def unlink_account(request, link_id):
    if request.method == 'POST':
        link_service.remove_link(link_id)
        return HttpResponseRedirect('/Admin/LinkedAccounts')
    else:
        user = AuthService.get_current_user(request)
        link = link_service.get_link(link_id)
        context = {
            'user': user,
            'email': link['email'],
            'o365Email': link['o365Email']
        }
        return render(request, 'admin/unlinkaccount.html', context)

@login_required
@admin_only
def add_app_role_assignments(request):
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.AADGraph, user.o365_user_id)
    aad_graph_service = AADGraphService(user.tenant_id, token)

    service_principal = aad_graph_service.get_service_principal()
    if not service_principal:
        request.session['Error'] = 'Could not found the service principal. Please provdie the admin consent.'
        return HttpResponseRedirect('/Admin')    
    count = aad_graph_service.add_app_role_assignments(service_principal['objectId'], service_principal['appDisplayName'])
    request.session["Message"] = 'User access was successfully enabled for %d user(s).' % count if count > 0 else 'User access was enabled for all users.'
    return HttpResponseRedirect("/Admin")

@login_required
@admin_only
def clear_login_cache(request):
    token_service.clear_token_cache()
    request.session["Message"] = 'Login cache cleared successfully!'
    return HttpResponseRedirect("/Admin")