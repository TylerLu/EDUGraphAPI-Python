'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings


import constant
from decorator import admin_only, login_required
from services.auth_service import get_user
from services.token_service import TokenService
from services.ms_graph_service import MSGraphService
from services.aad_graph_service import AADGraphService
from services.o365_user_service import O365UserService
from services.local_user_service import LocalUserService

LOCAL_USER = LocalUserService()
TOKEN_SERVICE = TokenService()

@login_required
@admin_only
def admin(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = get_user()
    LOCAL_USER.check_admin(user_info)
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    if request.session['Message']:
        parameter['message'] = request.session['Message'].split('\r\n')
        request.session['Message'] = ''
    return render(request, 'admin/index.html', parameter)

@login_required
@admin_only
def linked_accounts(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = get_user()
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
    user_info = get_user()
    parameter = {}
    parameter['links'] = links
    if request.method == 'POST':
        LOCAL_USER.remove_link(link_id)
        user_links = LOCAL_USER.get_links(user_info['tenant_id'])
        parameter['user_links'] = user_links
        return render(request, 'admin/linkaccounts.html', parameter)
    else:
        email, o365Email = LOCAL_USER.get_link(link_id)
        parameter['email'] = email
        parameter['o365Email'] = o365Email
        return render(request, 'admin/unlinkaccounts.html', parameter)

@login_required
@admin_only
def consent(request):
    scheme = request.scheme
    host = request.get_host()
    redirect_uri = '%s://%s/Admin/ProcessCode' % (scheme, host)
    consent_url = constant.admin_consent_url + redirect_uri
    return HttpResponseRedirect(consent_url)

def process_code(request):
    scheme = request.scheme
    host = request.get_host()
    redirect_uri = '%s://%s/Admin/ProcessCode' % (scheme, host)
    code = request.GET.get('code', '')

    aad_auth_result = TOKEN_SERVICE.get_token_with_code(code, redirect_uri, constant.Resources.AADGraph)
    o365_user_id = aad_auth_result.get('oid')    
    organzation_id = '64446b5c-6d85-4d16-9ff2-94eddc0c2439'
    aad_token = TOKEN_SERVICE.cache_tokens(aad_auth_result, o365_user_id)
    ms_token = TOKEN_SERVICE.get_access_token(constant.Resources.MSGraph, o365_user_id)

    ms_graph_service = MSGraphService(access_token=ms_token)
    graph_user = ms_graph_service.get_me()
    graph_org = ms_graph_service.get_organization(organzation_id)
    
    aad_graph_service = AADGraphService(graph_org['id'], aad_token)
    admin_ids = aad_graph_service.get_admin_ids()
    license_ids = aad_graph_service.get_license_ids()

    o365_user_service = O365UserService()
    user_info = o365_user_service.get_client_user(graph_user, graph_org, admin_ids, license_ids)

    LOCAL_USER.update_organization(user_info, True)
    LOCAL_USER.check_link_status(user_info)

    request.session['Message'] = 'Admin consented successfully!'
    return HttpResponseRedirect('/Admin')

@login_required
@admin_only
def unconsent(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = get_user()

    LOCAL_USER.update_organization(user_info, False)
    LOCAL_USER.remove_links(user_info['tenant_id'])
    
    token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user_info['uid'])
    aad_graph_service = AADGraphService(user_info['tenant_id'], token)
    app_id = aad_graph_service.get_app_id()
    aad_graph_service.delete_app(app_id)

    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    request.session['Message'] = 'Admin unconsented successfully!'
    return HttpResponseRedirect('/Admin')

def add_app_roles(request):
    user_info = get_user()
    token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user_info['uid'])
    aad_graph_service = AADGraphService(user_info['tenant_id'], token)
    app_id = aad_graph_service.get_app_id()
    app_name = aad_graph_service.get_app_name()

    if not app_id:
        request.session['Error'] = 'Could not found the service principal. Please provdie the admin consent.'
        return HttpResponseRedirect('/Admin')
    
    aad_graph_service.add_app_users(app_id, app_name)
    count = 0
    request.session["Message"] = 'User access was successfully enabled for %d user(s).' % count if count > 0 else 'User access was enabled for all users.'
    return HttpResponseRedirect("/Admin");

def consent_alone(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = get_user()
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

