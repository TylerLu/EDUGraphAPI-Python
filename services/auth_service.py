import urllib
import constant
import uuid
import jwt
import requests
'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
class AuthUser(object):
    is_local = False
    is_admin = False
    are_linked = False
    is_student = False
    local_existed = False
    is_in_a_school = False
    is_authenticated = False
    is_admin_consented = False

    uid = ''
    role = ''
    mail = ''
    email = ''
    photo = ''
    color = ''
    o365Email = ''
    last_name = ''
    tenant_id = ''
    school_id = ''
    school_uid = ''
    first_name = ''
    tenant_name = ''
    display_name = ''
    local_message = ''
    class_object_id = ''
    school_object_id = ''

def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

@singleton
class AuthService(object):
    def __init__(self):
        user_obj = AuthUser()
        self.user = dict((name, getattr(user_obj, name)) for name in dir(user_obj) if not name.startswith('__')  and not callable(getattr(user_obj, name)))

    def login(self, request, user):
        if not user:
            setattr(request, 'user', self.user)
        else:
            for key in user:
                self.user[key] = user[key]
            setattr(request, 'user', self.user)

    def get_user(self):
        return self.user

    def logoff(self, request):
        self.user = {}
        setattr(request, 'user', self.user)

def login(request, user=None):
    auth_service = AuthService()
    auth_service.login(request, user)

def logout(request):
    auth_service = AuthService()
    auth_service.logoff(request)

def get_user():
    auth_service = AuthService()
    return auth_service.get_user()

def authenticate(user_info):
    if user_info.get('uid') and user_info.get('tenant_id'):
        return True
    return False

def get_redirect_uri(request, relative_redirect_uri):
    scheme = request.scheme
    host = request.get_host()
    return '%s://%s/%s' % (scheme, host, relative_redirect_uri)

def get_authorization_url(request, response_type, relative_redirect_uri, state, extra_params = None):  
    params  = { 
        'client_id' : constant.client_id, 
        'response_type': response_type,
        'response_mode': 'form_post',
        'redirect_uri': get_redirect_uri(request, relative_redirect_uri),
        'state': state
        }
    if extra_params:
        params.update(extra_params)    
    request.session['auth_state'] = state    
    nonce = params.get('nonce')
    if nonce:
        request.session['auth_nonce'] = nonce
    return constant.login_base_uri + urllib.parse.urlencode(params).replace('%2B', '+')


def get_random_string():
    return uuid.uuid4().hex

def validate_state(request):
    if request.POST.get('state') != request.session['auth_state']:
        raise Exception('state does not match')

def get_id_token(request):
    id_token = request.POST.get('id_token')
    return jwt.decode(id_token, verify=False)