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
        
    def __init__(self, access_token):
        self.access_token = access_token
        self.api_base_uri = constant.Resources.MSGraph + 'v1.0' + '/'
        self.rest_api_service = RestApiService()

        auth_provider = AuthProvider()
        auth_provider.access_token(self.access_token)
        self.ms_graph_client = msgraph.GraphServiceClient(self.api_base_uri, auth_provider, msgraph.HttpProvider())

    def get_me(self):
        return self.ms_graph_client.me.get()

    def get_organization(self, tenant_id):
        # The following code will throw an exception: name 'AssignedPlansCollectionPage' is not defined
        #     return self.ms_graph_client.organization[tenant_id].get()
        # It is a bug of the Microsoft Graph SDK for Python. We use the REST API directly.
        url = self.api_base_uri + 'organization/' + tenant_id
        return self.rest_api_service.get_json(url, self.access_token)

    def get_photo(self, object_id):
        url = self.api_base_uri + 'users/%s/photo/$value' % object_id
        try:
            return self.rest_api_service.get_img(url, self.access_token)
        except:
            return None

    def get_documents(self, object_id):
        url = self.api_base_uri + 'groups/%s/drive/root/children' % object_id
        return self.rest_api_service.get_object_list(url, self.access_token, model=Document)
    
    def get_documents_root(self, object_id):
        url = self.api_base_uri + 'groups/%s/drive/root' % object_id
        document = self.rest_api_service.get_object(url, self.access_token, model=Document)
        return document['web_url']

    def get_conversations(self, object_id, section_mail):
        url = self.api_base_uri + 'groups/%s/conversations' % object_id
        conversations_list = self.rest_api_service.get_object_list(url, self.access_token, model=Conversation)
        for conversation in conversations_list:
            conversation['url'] = conversation['url'] % section_mail
        return conversations_list
    
    def get_conversations_root(self, section_email):
        return 'https://outlook.office.com/owa/?path=/group/%s/mail&exsvurl=1&ispopout=0' % section_email
