'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import re
import constant
from services.rest_api_service import RestApiService
from models.education import School, Section, EduUser

class EducationService(object):

    def __init__(self, tenant_id, access_token):
        self.api_base_uri = constant.Resources.MSGraph + '/' + constant.Resources.MSGraph_VERSION + '/'
        self.access_token = access_token
        self.rest_api_service = RestApiService()
        self.skip_token_re = re.compile('\$skiptoken=.*')

    def get_my_school_id(self):
        url = self.api_base_uri + 'me'
        user_content = self.rest_api_service.get_json(url, self.access_token)
        school_id = user_content.get('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId', '')
        return school_id

    def get_school_user_id(self):
        url = self.api_base_uri + 'me'
        user_content = self.rest_api_service.get_json(url, self.access_token)
        sid = user_content.get('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_StudentId', '')
        tid = user_content.get('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_TeacherId', '')
        if sid:
            return sid
        elif tid:
            return tid

    def get_schools(self):
        '''
        Get all schools that exist in the Azure Active Directory tenant.
        '''
        url = self.api_base_uri + 'administrativeUnits'
        return self.rest_api_service.get_object_list(url, self.access_token, model=School)

    def get_school(self, object_id):
        '''
        Get a school by using the object_id.
        <param name="object_id">The Object ID of the school administrative unit in Azure Active Directory.</param>
        '''
        url = self.api_base_uri + 'administrativeUnits/%s' % object_id
        return self.rest_api_service.get_object(url, self.access_token, model=School)

    def get_section_members(self, section_object_id):
        '''
        Get a section members by using the object_id.
        <param name="section_object_id">The Object ID of the section.</param>
        <param name="object_type">The members type.</param>
        '''
        url = self.api_base_uri + 'groups/%s?$expand=members' % section_object_id
       
        return self.rest_api_service.get_object_list(url, self.access_token, key='members', model=EduUser)

    def get_my_sections(self, school_id):
        '''
        Get my sections within a school
        <param name="school_id">The school id.</param>
        '''
        url = self.api_base_uri + 'me/memberOf'        
        section_list = self.rest_api_service.get_object_list(url, self.access_token, model=Section)
        mysection_list = [s for s in section_list if s.education_object_type == 'Section' and s.school_id == school_id ]
      
        for section in mysection_list:
            section.members = self.get_section_members(section.object_id)
                
        mysection_list.sort(key=lambda d:d.combined_course_number)
        return mysection_list

    def get_sections(self, school_id, top=12, nextlink=''):
        '''
        Get sections within a school
        <param name="school_id">The school id.</param>
        <param name="mysection_emails">All my section's email</param>
        <param name="top">Get record number from API</param>
        <param name="nextlink">Get skiptoken from nextlink</param>
        '''
        skiptoken = self._get_skip_token(nextlink)
        url = self.api_base_uri + "groups?$filter=extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType eq 'Section' and extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId eq '%s'&$top=%s%s" % (school_id, top, skiptoken)

        return self.rest_api_service.get_object_list(url, self.access_token, model=Section, next_key='@odata.nextLink')

    def get_section(self, object_id):
        '''
        Get a section by using the object_id.
        <param name="object_id">The Object ID of the section.</param>
        '''
        url = self.api_base_uri + 'groups/%s' % object_id
        return self.rest_api_service.get_object(url, self.access_token, model=Section)

    def get_members(self, object_id, top=12, nextlink=''):
        '''
        Get members within a school
        <param name="object_id">The Object ID of the school.</param>
        <param name="top">Get record number from API</param>
        <param name="nextlink">Get skiptoken from nextlink</param>
        '''
        skiptoken = self._get_skip_token(nextlink)
        url = self.api_base_uri + 'administrativeUnits/%s/members?$top=%s%s' % (object_id, top, skiptoken)
        return self.rest_api_service.get_object_list(url, self.access_token, model=EduUser, next_key='@odata.nextLink')

    def get_students(self, school_id, top=12, nextlink=''):
        '''
        Get students within a school
        <param name="school_id">The school id.</param>
        <param name="top">Get record number from API</param>
        <param name="nextlink">Get skiptoken from nextlink</param>
        '''
        skiptoken = self._get_skip_token(nextlink)
        url = self.api_base_uri + "users?$filter=extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId eq '%s' and extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType eq 'Student'&$top=%s%s" % (school_id, top, skiptoken)
        return self.rest_api_service.get_object_list(url, self.access_token, model=EduUser, next_key='@odata.nextLink')
    
    def get_teachers(self, school_id, top=12, nextlink=''):
        '''
        Get teachers within a school
        <param name="school_id">The school id.</param>
        <param name="top">Get record number from API</param>
        <param name="nextlink">Get skiptoken from nextlink</param>
        '''
        skiptoken = self._get_skip_token(nextlink)
        url = self.api_base_uri + "users?$filter=extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId eq '%s' and extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType eq 'Teacher'&$top=%s%s" % (school_id, top, skiptoken)
        
        return self.rest_api_service.get_object_list(url, self.access_token, model=EduUser, next_key='@odata.nextLink')

    def _get_skip_token(self, nextlink):
        if nextlink and nextlink.find('skiptoken') != -1:
            link_skiptoken = self.skip_token_re.findall(nextlink)[0]
            return '&%s' % link_skiptoken
        return ''
