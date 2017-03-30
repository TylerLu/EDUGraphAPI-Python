"""
MS Graph Api Request Class
"""
import adal
import msgraph

class MSGraphRequest(object):
    
    def __init__(self, client_id, client_secret, authorize_token_uri, graph_base_uri,):
        self.client_id = client_id
        self.client_secret = client_secret
        self.context = adal.AuthenticationContext(authorize_token_uri)
        self.http_provider = msgraph.HttpProvider()
        self.auth_provider = msgraph.AuthProvider()
        self.graph_base_uri = graph_base_uri
    
    def authorize(self, code, redirect_uri, resource):
        result = self.context.acquire_token_with_authorization_code(code, redirect_uri, resource, self.client_id, self.client_secret)
        return result
    
    def authorize_refresh(self, refresh_token, resource):
        result = self.context.acquire_token_with_refresh_token(refresh_token, self.client_id, resource, self.client_secret)
        return result
    
    def get_client(self, token):
        self.auth_provider.access_token(token)
        client = msgraph.GraphServiceClient(self.graph_base_uri, self.auth_provider, self.http_provider)
        return client

    def send(self, url, token):
        key = 'Authorization'
        value = 'Bearer {0}'.format(token)
        self._headers[key] = value
        session = requests.Session()
        request_url = self._base_uri + self._url + '?api-version=1.6'
        request = requests.Request(self._method, request_url, self._headers)
        prepped = request.prepare()
        response = session.send(prepped)
        return response
