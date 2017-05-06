'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
import re
import constant
from services.rest_api_service import RestApiService
from schools.models import School, Section, EduUser

class EducationService(object):

    def __init__(self, tenant_id, access_token):
        self.api_base_uri = constant.Resources.AADGraph + tenant_id + '/'
        self.access_token = access_token
        self.rest_api_service = RestApiService()
        self.skip_token_re = re.compile('\$skiptoken=.*')

    def get_my_school_id(self):
        url = self.api_base_uri + 'me?api-version=1.6'
        user_content = self.rest_api_service.get_json(url, self.access_token)
        school_id = user_content.get('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId', '')
        return school_id

    def get_school_user_id(self):
        school_uid = ''
        url = self.api_base_uri + 'me?api-version=1.6'
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
        url = self.api_base_uri + 'administrativeUnits?api-version=beta'
        return self.rest_api_service.get_object_list(url, self.access_token, model=School)

    def get_school(self, object_id):
        '''
        Get a school by using the object_id.
        <param name="object_id">The Object ID of the school administrative unit in Azure Active Directory.</param>
        '''
        school_result = {}
        url = self.api_base_uri + 'administrativeUnits/%s?api-version=beta' % object_id
        school_result = self.rest_api_service.get_object(url, self.access_token, model=School)
        return school_result

    def get_section_members(self, section_object_id, object_type=''):
        '''
        Get a section members by using the object_id.
        <param name="section_object_id">The Object ID of the section.</param>
        <param name="object_type">The members type.</param>
        '''
        member_list = []
        url = self.api_base_uri + 'groups/%s/members?api-version=1.5' % section_object_id
        members = self.rest_api_service.get_object_list(url, self.access_token, model=EduUser)
        if object_type:
            member_list = [i for i in members if i['object_type'] == object_type]
        else:
            member_list = members
        return member_list

    def get_my_sections(self, school_id):
        '''
        Get my sections within a school
        <param name="school_id">The school id.</param>
        '''
        url = self.api_base_uri + 'me/memberOf?api-version=1.5'        
        section_list = self.rest_api_service.get_object_list(url, self.access_token, model=Section)
        mysection_list = [s for s in section_list if s.get('education_object_type') == 'Section' and s.get('school_id') == school_id ]
      
        for section in mysection_list:
            section['teachers'] = self.get_section_members(section['object_id'], 'Teacher')
                
        mysection_list.sort(key=lambda d:d['combined_course_number'])
        return mysection_list

    def get_all_sections(self, school_id, top=12, nextlink=''):
        '''
        Get sections within a school
        <param name="school_id">The school id.</param>
        <param name="mysection_emails">All my section's email</param>
        <param name="top">Get record number from API</param>
        <param name="nextlink">Get skiptoken from nextlink</param>
        '''
        skiptoken = ''
        if nextlink and nextlink.find('skiptoken') != -1:
            link_skiptoken = self.skip_token_re.findall(nextlink)[0]
            skiptoken = '&%s' % link_skiptoken

        sections_list = []
        next_link = ''
        url = self.api_base_uri + "groups?api-version=1.5&$filter=extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType eq 'Section' and extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId eq '%s'&$top=%s%s" % (school_id, top, skiptoken)
        section_list, next_link = self.rest_api_service.get_object_list(url, self.access_token, model=Section, next_key='odata.nextLink')
        return section_list, next_link

    def get_section(self, object_id):
        '''
        Get a section by using the object_id.
        <param name="object_id">The Object ID of the section.</param>
        '''
        section_result = {}
        version = '?api-version=1.5'
        url = self.api_base_uri + 'groups/%s' % object_id + version
        section_result = self.rest_api_service.get_object(url, self.access_token, model=Section)
        return section_result

    def get_members(self, object_id, top=12, nextlink=''):
        '''
        Get members within a school
        <param name="object_id">The Object ID of the school.</param>
        <param name="top">Get record number from API</param>
        <param name="nextlink">Get skiptoken from nextlink</param>
        '''
        skiptoken = ''
        if nextlink and nextlink.find('skiptoken') != -1:
            link_skiptoken = self.skip_token_re.findall(nextlink)[0]
            skiptoken = '&%s' % link_skiptoken
        members_list = []
        next_link = ''
        url = self.api_base_uri + 'administrativeUnits/%s/members?api-version=beta&$top=%s%s' % (object_id, top, skiptoken)
        members_list, next_link = self.rest_api_service.get_object_list(url, self.access_token, model=EduUser, next_key='odata.nextLink')
        return members_list, next_link

    def get_students(self, school_id, top=12, nextlink=''):
        '''
        Get students within a school
        <param name="school_id">The school id.</param>
        <param name="top">Get record number from API</param>
        <param name="nextlink">Get skiptoken from nextlink</param>
        '''
        skiptoken = ''
        if nextlink and nextlink.find('skiptoken') != -1:
            link_skiptoken = self.skip_token_re.findall(nextlink)[0]
            skiptoken = '&%s' % link_skiptoken
        students_list = []
        next_link = ''
        url = self.api_base_uri + "users?api-version=1.5&$filter=extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId eq '%s' and extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType eq 'Student'&$top=%s%s" % (school_id, top, skiptoken)
        students_list, next_link = self.rest_api_service.get_object_list(url, self.access_token, model=EduUser, next_key='odata.nextLink')
        return students_list, next_link

    def get_teachers(self, school_id, top=12, nextlink=''):
        '''
        Get teachers within a school
        <param name="school_id">The school id.</param>
        <param name="top">Get record number from API</param>
        <param name="nextlink">Get skiptoken from nextlink</param>
        '''
        skiptoken = ''
        if nextlink and nextlink.find('skiptoken') != -1:
            link_skiptoken = self.skip_token_re.findall(nextlink)[0]
            skiptoken = '&%s' % link_skiptoken
        teachers_list = []
        next_link = ''
        url = self.api_base_uri + "users?api-version=1.5&$filter=extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId eq '%s' and extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType eq 'Teacher'&$top=%s%s" % (school_id, top, skiptoken)
        teachers_list, next_link = self.rest_api_service.get_object_list(url, self.access_token, model=EduUser, next_key='odata.nextLink')
        return teachers_list, next_link

    def get_my_groups(self, school_id):
        '''
        Get my groups
        <param name="school_id">The school id.</param>
        '''
        groups_list = []
        url = self.api_base_uri + 'me/memberOf?api-version=1.5'
        group_list = self.rest_api_service.get_object_list(url, self.access_token, model=Section)
        for section in group_list:
            if section['school_id'] == school_id:
                groups_list.append(section['display_name'])
        return groups_list