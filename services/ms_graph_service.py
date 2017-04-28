'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
import msgraph
import constant
from utils.auth_provider import AuthProvider
from services.rest_api_service import RestApiService
from schools.models import Document, Conversation

class MSGraphService(object):
    
    def __init__(self, token, tenant_id=''):
        self.http_provider = msgraph.HttpProvider()
        self.auth_provider = AuthProvider()

        self.api_base_uri = constant.Resources.MSGraph + '/v1.0/' + tenant_id
        self.token = token
        self.rest_api_service = RestApiService()
        
    def get_client(self):
        self.auth_provider.access_token(self.token)
        client = msgraph.GraphServiceClient(self.api_base_uri, self.auth_provider, self.http_provider)
        return client
    
    def get_photo(self, object_id):
        photo = ''
        url = self.api_base_uri + 'users/%s/photo/$value' % object_id
        photo_content = self.rest_api_service.get_img(url, self.token)
        if photo_content:
            photo = photo_content
        return photo

    def get_documents(self, object_id):
        documents_list = []
        url = self.api_base_uri + 'groups/%s/drive/root/children' % object_id
        documents_list = self.rest_api_service.get_object_list(url, self.token, model=Document)
        return documents_list
    
    def get_documents_root(self, object_id):
        documents_root = ''
        url = self.api_base_uri + 'groups/%s/drive/root' % object_id
        document = self.rest_api_service.get_object(url, self.token, model=Document)
        documents_root = document['web_url']
        return documents_root

    def get_conversations(self, object_id, section_mail):
        conversations_list = []
        url = self.api_base_uri + 'groups/%s/conversations' % object_id
        conversations_list = self.rest_api_service.get_object_list(url, self.token, model=Conversation)
        for conversation in conversations_list:
            conversation['url'] = conversation['url'] % section_mail
        return conversations_list
    
    def get_conversations_root(self, section_email):
        seeall_url = 'https://outlook.office.com/owa/?path=/group/%s/mail&exsvurl=1&ispopout=0' % section_email
        return seeall_url

