"""
MS Graph Api Request Class
"""
import adal
import json
import msgraph
import requests
import constant
from msgraph.options import QueryOption
from msgraph.model.assigned_license import AssignedLicense 

class MSGraphRequest(object):
    
    def __init__(self):
        self.client_id = constant.client_id
        self.client_secret = constant.client_secret
        self.context = adal.AuthenticationContext(constant.authorize_token_uri)
        self.http_provider = msgraph.HttpProvider()
        self.auth_provider = msgraph.AuthProvider()
        self.graph_base_uri = constant.graph_base_uri
    
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

    def send(self, url, token, data=''):
        if data == 'img':
            headers = {'content-type': 'image/jpeg'}
        else:
            headers = {'Accept': 'application/json',
                       'Content-Type': 'application/json'}
        key = 'Authorization'
        value = 'Bearer {0}'.format(token)
        headers[key] = value
        base_uri = 'https://graph.microsoft.com/v1.0/'
        session = requests.Session()
        request_url = base_uri + url
        request = requests.Request('GET', request_url, headers)
        prepped = request.prepare()
        response = session.send(prepped)
        content = ''
        if response.status_code == 200:
            if data == 'img':
                content = response.content
            else:
                content = json.loads(response.text)
        else:
            print(url, response.status_code)
        return content
    
    def get_user_photo(self, token, object_id):
        photo = ''
        try:
            url = 'users/%s/photo/$value' % object_id
            photo_content = self.send(url, token, 'img')
            if photo_content:
                photo = photo_content
        except:
            pass
        return photo

    def get_documents_for_section(self, token, object_id):
        documents_list = []
        try:
            url = 'groups/%s/drive/root/children' % object_id
            documents_content = self.send(url, token)
            documents_list = documents_content['value']
        except:
            pass
        return documents_list
    
    def get_documents_root(self, token, object_id):
        documents_root = ''
        try:
            url = 'groups/%s/drive/root' % object_id
            root_content = self.send(url, token)
            documents_root = root_content['webUrl']
        except:
            pass
        return documents_root

    def get_conversatoins_for_section(self, token, object_id):
        conversations_list = []
        try:
            url = 'groups/%s/conversations' % object_id
            conversations_content = self.send(url, token)
            conversations_list = conversations_content['value']
        except:
            pass
        return conversations_list

