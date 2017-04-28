'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
import re
import constant
from services.rest_api_service import RestApiService
from schools.models import School, Section, EduUser

class EducationService(object):

    def __init__(self, tenant_id, token):
        self.api_base_uri = constant.Resources.AADGraph + '/' + tenant_id + '/'
        self.token = token
        self.rest_api_service = RestApiService()
        self._token_re = re.compile('\$skiptoken=.*')
    
    def get_schools(self, school_uid=''):
        '''
        Get all schools that exist in the Azure Active Directory tenant. 
        '''
        schools_list = []
        version = '?api-version=beta'
        url = self.api_base_uri + 'administrativeUnits' + version
        school_list = self.rest_api_service.get_object_list(url, self.token, model=School)
        out_schools = self._normalize_schools(school_list, school_uid)
        return out_schools
    
    def get_school(self, object_id):
        '''
        Get a school by using the object_id.
        <param name="object_id">The Object ID of the school administrative unit in Azure Active Directory.</param>
        '''
        school_result = {}
        version = '?api-version=beta'
        url = self.api_base_uri + 'administrativeUnits/%s' % object_id + version
        school_result = self.rest_api_service.get_object(url, self.token, model=School)
        return school_result
    
    def get_section_members(self, section_object_id, object_type=''):
        '''
        Get a section members by using the object_id.
        <param name="section_object_id">The Object ID of the section.</param>
        <param name="object_type">The members type.</param>
        '''
        member_list = []
        version = '?api-version=1.5'
        url = self.api_base_uri + 'groups/%s/members' % section_object_id + version
        members = self.rest_api_service.get_object_list(url, self.token, model=EduUser)
        if object_type:
            member_list = [i for i in members if i['object_type'] == object_type]
        else:
            member_list = members
        return member_list

    def _get_my_sections(self, load_members=False):
        '''
        Get my sections
        <param name="load_members">Include members or not.</param>
        '''
        mysection_list = []
        version = '?api-version=1.5'
        url = self.api_base_uri + 'me/memberOf' + version
        section_list = self.rest_api_service.get_object_list(url, self.token, model=Section)

        for section in section_list:
            if load_members:
                member_list = self.get_section_members(self.token, section['object_id'])
                section['teachers'] =  [i for i in member_list if i['object_type'] == 'Teacher']
            mysection_list.append(section)
        return mysection_list

    def get_my_sections(self, school_id):
        '''
        Get my sections within a school
        <param name="school_id">The school id.</param>
        '''
        section_list = self._get_my_sections(True)
        mysection_list = []
        mysection_emails = []

        for section in section_list:
            if section['school_id'] == school_id:
                mysection_list.append(section)
                mysection_emails.append(section['email'])
        mysection_list.sort(key=lambda d:d['combined_course_number'])
        return mysection_list, mysection_emails
    
    def get_all_sections(self, school_id, mysection_emails=[], top=12, nextlink=''):
        '''
        Get sections within a school
        <param name="school_id">The school id.</param>
        <param name="mysection_emails">All my section's email</param>
        <param name="top">Get record number from API</param>
        <param name="nextlink">Get skiptoken from nextlink</param>
        '''
        skiptoken = ''
        if nextlink and nextlink.find('skiptoken') != -1:
            link_skiptoken = self._token_re.findall(nextlink)[0]
            skiptoken = '&%s' % link_skiptoken
        sections_list = []
        next_link = ''
        url = self.api_base_uri + "groups?api-version=1.5&$filter=extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType eq 'Section' and extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId eq '%s'&$top=%s%s" % (school_id, top, skiptoken)
        section_list, next_link = self.rest_api_service.get_object_list(url, self.token, model=Section, next_key='odata.nextLink')
        out_sections = self._normalize_all_sections(section_list, mysection_emails)
        return out_sections, next_link

    def get_section(self, object_id):
        '''
        Get a section by using the object_id.
        <param name="object_id">The Object ID of the section.</param>
        '''
        section_result = {}
        version = '?api-version=1.5'
        url = self.api_base_uri + 'groups/%s' % object_id + version
        section_result = self.rest_api_service.get_object(url, self.token, model=Section)
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
            link_skiptoken = self._token_re.findall(nextlink)[0]
            skiptoken = '&%s' % link_skiptoken
        members_list = []
        next_link = ''
        url = self.api_base_uri + 'administrativeUnits/%s/members?api-version=beta&$top=%s%s' % (object_id, top, skiptoken)
        members_list, next_link = self.rest_api_service.get_object_list(url, self.token, model=EduUser, next_key='odata.nextLink')
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
            link_skiptoken = self._token_re.findall(nextlink)[0]
            skiptoken = '&%s' % link_skiptoken
        students_list = []
        next_link = ''
        url = self.api_base_uri + "users?api-version=1.5&$filter=extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId eq '%s' and extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType eq 'Student'&$top=%s%s" % (school_id, top, skiptoken)
        students_list, next_link = self.rest_api_service.get_object_list(url, self.token, model=EduUser, next_key='odata.nextLink')
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
            link_skiptoken = self._token_re.findall(nextlink)[0]
            skiptoken = '&%s' % link_skiptoken
        teachers_list = []
        next_link = ''
        url = self.api_base_uri + "users?api-version=1.5&$filter=extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId eq '%s' and extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType eq 'Teacher'&$top=%s%s" % (school_id, top, skiptoken)
        teachers_list, next_link = self.rest_api_service.get_object_list(url, self.token, model=EduUser, next_key='odata.nextLink')
        return teachers_list, next_link
    
    def get_my_groups(self, school_id):
        '''
        Get my groups
        <param name="school_id">The school id.</param>
        '''
        groups_list = []
        version = '?api-version=1.5'
        url = self.api_base_uri + 'me/memberOf' + version
        group_list = self.rest_api_service.get_object_list(url, self.token, model=Section)
        for section in group_list:
            if section['school_id'] == school_id:
                groups_list.append(section['display_name'])
        return groups_list

    def _normalize_schools(self, school_list, school_uid=''):
        out_schools = []
        temp_schools = []
        for school in school_list:
            if school_uid and school['id'] == school_uid:
                out_schools.append(school)
            else:
                temp_schools.append(school)
        temp_schools.sort(key=lambda d:d['name'])
        out_schools.extend(temp_schools)
        return out_schools
    
    def _normalize_all_sections(self, section_list, mysection_emails):
        out_sections = []
        for section in section_list:
            if section['email']  in mysection_emails:
                section['ismy'] = True
            else:
                section['ismy'] = False
            out_sections.append(section)
        return out_sections

