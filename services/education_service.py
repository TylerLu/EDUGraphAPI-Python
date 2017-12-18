'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import re
import constant
from services.rest_api_service import RestApiService
from models.education import School, Class, EduUser

class EducationService(object):

    def __init__(self, tenant_id, access_token):
        self.api_base_uri = constant.Resources.MSGraph + '/' + constant.Resources.MSGraph_VERSION + '/'
        self.access_token = access_token
        self.rest_api_service = RestApiService()
        self.skip_token_re = re.compile('(?<=skiptoken=).*')

    def get_me(self):
        url = self.api_base_uri + 'education/me?$expand=schools,classes'
        return self.rest_api_service.get_object(url, self.access_token, model=EduUser)

    def get_schools(self):
        '''
        Get all schools that exist in the Azure Active Directory tenant.
        '''
        url = self.api_base_uri + 'education/schools'
        return self.rest_api_service.get_object_list(url, self.access_token, model=School)

    def get_school(self, school_id):
        '''
        Get a school by using the object_id.
        '''
        url = self.api_base_uri + 'education/schools/%s' % school_id
        return self.rest_api_service.get_object(url, self.access_token, model=School)

    def get_my_classes(self, school_id=None):
        '''
        Get my classes within a school
        <param name="school_id">The school id.</param>
        '''
        url = self.api_base_uri + 'education/me/classes?$expand=schools'           
        classes = self.rest_api_service.get_object_list(url, self.access_token, model=Class)
        if school_id:
            classes = [c for c in classes if any(s.id == school_id for s in c.schools)]
      
        for c in classes:
            c.members = self.get_class_members(c.id)
                
        classes.sort(key=lambda c:c.code)        
        return classes

    def get_classes(self, school_id, top=12, nextlink=''):
        '''
        Get classes within a school
        <param name="school_id">The school id.</param>
        <param name="mysection_emails">All my section's email</param>
        <param name="top">Get record number from API</param>
        <param name="nextlink">Get skiptoken from nextlink</param>
        '''
        skiptoken = self._get_skip_token(nextlink)
        url = self.api_base_uri + "education/schools/%s/classes?$expand=schools&$top=%s&skiptoken=%s" % (school_id, top, skiptoken)
        return self.rest_api_service.get_object_list(url, self.access_token, model=Class, next_key='@odata.nextLink')

    def get_class(self, class_id):
        '''
        Get a section by using the object_id.
        <param name="object_id">The Object ID of the section.</param>
        '''
        url = self.api_base_uri + "education/classes/%s" % class_id
        return self.rest_api_service.get_object(url, self.access_token, model=Class)

    def get_class_members(self, class_id):
        '''
        Get a class members by using the object_id.
        <param name="class_id">The Object ID of the section.</param>
        <param name="object_type">The members type.</param>
        '''
        url = self.api_base_uri + 'education/classes/%s/members' % class_id       
        return self.rest_api_service.get_object_list(url, self.access_token, model=EduUser)

    def get_teachers(self, school_id):
        '''
        Get teachers within a school
        '''
        url = self.api_base_uri + "users?$filter=extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId eq '%s' and extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType eq 'Teacher'" % school_id        
        return self.rest_api_service.get_object_list(url, self.access_token, model=EduUser)

    def add_member(self, class_id, user_id):
        '''
        Add a user to members of a class.
        Reference URL: https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/api/group_post_members
        '''
        url = self.api_base_uri + "groups/" + class_id + "/members/$ref"
        data ={'@odata.id':'https://graph.microsoft.com/v1.0/directoryObjects/'+user_id}  
        return self.rest_api_service.post_json(url,self.access_token,None,data)

    def add_owner(self, class_id, user_id):
        '''
        Add a user to owner of a class.
        Reference URL: https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/api/group_post_owners
        '''
        url = self.api_base_uri + "groups/" + class_id + "/owners/$ref"
        data ={'@odata.id':'https://graph.microsoft.com/v1.0/users/'+user_id}  
        return self.rest_api_service.post_json(url,self.access_token,None,data)

    def _get_skip_token(self, nextlink):
        if nextlink:
            matches = self.skip_token_re.findall(nextlink)
            if matches:
                return matches[0]
        return ''
