from utils.token_controller import TokenManager

class TokenInfo(object):
    access_token = ''
    refresh_token = ''
    expires_on = ''
    resource = ''

class TokenRefreshBackend(object):
    """
    Authenticates token valid
    """
    def __init__(self):
        self._token_manager = TokenManager()
        
    def authenticate(self, access_token='', refresh_token='', expires='', token_resource='', resource=''):
        token_obj = TokenInfo()
        if not access_token or not refresh_token:
            return token_obj
        if token_resource == resource and self._token_manager.check(expires):
            token_obj.access_token = access_token
            token_obj.refresh_token = refresh_token
            token_obj.expires_on = expires
            token_obj.resource = resource
        else:
            access_token, refresh_token, expires_on = self._token_manager.get_token(refresh_token, resource)
            token_obj.access_token = access_token
            token_obj.refresh_token = refresh_token
            token_obj.expires_on = expires
            token_obj.resource = resource
        return token_obj

class TokenByCodeBackend(object):
    
    def __init__(self):
        self._token_manager = TokenManager()

    def authenticate(self, code='', resource=''):
        token_obj = TokenInfo()
        if not code or not resource:
            return token_obj
        access_token, refresh_token, expires_on = self._token_manager.get_token_by_code(code, resource)
        token_obj.access_token = access_token
        token_obj.refresh_token = refresh_token
        token_obj.expires_on = expires_on
        token_obj.resource = resource
        return token_obj


