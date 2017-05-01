'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

@singleton
class AuthService(object):
    user = {}
    def login(self, request, user):
        if not user:
            setattr(request, 'user', self.user)
        else:
            self.user = user
            setattr(request, 'user', user)

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
