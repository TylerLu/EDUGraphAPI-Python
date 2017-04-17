"""
AAD Graph Api Request Class
"""
import re
import json
import requests
import constant

class AADGraphRequest(object):
    
    def __init__(self, method='GET', headers=None, token=''):
        self._base_uri = 'https://graph.windows.net/canvizEDU.onmicrosoft.com/'
        self._method = method
        self._headers = headers
        self._headers = {'Accept': 'application/json',
                         'Content-Type': 'application/json'}
        if headers:
            self._headers.update(headers)

        self._access_token = token
        
        self._token_re = re.compile('\$skiptoken=.*')

    def set_method(self, value):
        self._method = value

    def set_headers(self, value):
        self._headers = value
    
    def set_access_token(self, value):
        self._access_token = value

    def send(self, url, token, version='?api-version=1.6'):
        key = 'Authorization'
        value = 'Bearer {0}'.format(token)
        self._headers[key] = value
        session = requests.Session()
        request_url = self._base_uri + url + version
        request = requests.Request(self._method, request_url, self._headers)
        prepped = request.prepare()
        response = session.send(prepped)
        content = ''
        if response.status_code == 200:
            content = json.loads(response.text)
        else:
            print(response.text)
        return content
    
    def get_admin_ids(self, token):
        admin_ids = set()
        try:
            url = 'directoryRoles'
            roles_content = self.send(url, token)
            roles_list = roles_content['value']
            id_list = set()
            for role in roles_list:
                if role['displayName'] == constant.company_admin_role_name:
                    id_list.add(role['objectId'])
            url = 'directoryRoles/%s/members'
            for id in id_list:
                members_url = url % id
                members_content = self.send(members_url, token)
                members_list = members_content['value']
                for member in members_list:
                    admin_ids.add(member['objectId'])
        except:
            pass
        return admin_ids

    def get_user_extra_info(self, token):
        sku_ids = set()
        uid = ''
        school_uid = ''
        school_id = ''
        extra_info = {}
        try:
            url = 'me'
            user_content = self.send(url, token)
            uid = user_content['objectId']
            licenses_list = user_content['assignedLicenses']
            for license in licenses_list:
                sku_ids.add(license['skuId'])
            sid = user_content.get('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_StudentId', '')
            tid = user_content.get('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_TeacherId', '')
            if sid:
                school_uid = sid
            elif tid:
                school_uid = tid
            school_id = user_content.get('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId', '')
        except:
            pass
        extra_info['uid'] = uid
        extra_info['sku_ids'] = sku_ids
        extra_info['school_uid'] = school_uid
        extra_info['school_id'] = school_id
        return extra_info
    
    def get_schoold_uid(self, token):
        try:
            url = 'me'
            user_content = self.send(url, token)
            licenses_list = user_content['assignedLicenses']
            for license in licenses_list:
                sku_ids.add(license['skuId'])
        except:
            pass
        return sku_ids

    def get_all_schools(self, token):
        schools_list = []
        try:
            url = 'administrativeUnits'
            version = '?api-version=beta'
            schools_content = self.send(url, token, version)
            schools_list = schools_content['value']
        except:
            pass
        return schools_list
    
    def get_one_school(self, token, object_id):
        school_result = {}
        try:
            url = 'administrativeUnits/%s' % object_id
            version = '?api-version=beta'
            school_content = self.send(url, token, version)
            school_result = school_content
        except:
            pass
        return school_result

    def get_sections_by_schoolid(self, token, schoolid, top=12, nextlink=''):
        skiptoken = ''
        if nextlink and nextlink.find('skiptoken') != -1:
            link_skiptoken = self._token_re.findall(nextlink)[0]
            skiptoken = '&%s' % link_skiptoken
        sections_list = []
        next_link = ''
        try:
            url = "groups?api-version=1.5&$filter=extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType eq 'Section' and extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId eq '%s'&$top=%s%s" % (schoolid, top, skiptoken)
            version = ''
            sections_content = self.send(url, token, version)
            sections_list = sections_content['value']
            next_link = sections_content.get('odata.nextLink', '')
        except:
            pass
        return sections_list, next_link

    def get_section_by_member(self, token):
        mysection_list = []
        url = 'me/memberOf'
        version = '?api-version=1.5'
        mysections_content = self.send(url, token, version)
        mysections_list = mysections_content['value']
        return mysections_list

    def get_one_section(self, token, object_id):
        section_result = {}
        try:
            url = 'groups/%s' % object_id
            version = '?api-version=1.5'
            section_content = self.send(url, token, version)
            section_result = section_content
        except:
            pass
        return section_result

    def get_teachers_for_section(self, token, object_id):
        teachers_list = []
        try:
            url = 'groups/%s/members' % object_id
            version = '?api-version=1.5'
            teachers_content = self.send(url, token, version)
            teachers_temp_list = teachers_content['value']
            teachers_list = [i for i in teachers_temp_list if i['extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType'] == 'Teacher']
        except:
            pass
        return teachers_list
    
    def get_students_for_section(self, token, object_id):
        students_list = []
        try:
            url = 'groups/%s/members' % object_id
            version = '?api-version=1.5'
            students_content = self.send(url, token, version)
            students_temp_list = students_content['value']
            students_list = [i for i in students_temp_list if i['extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType'] == 'Student']
        except:
            pass
        return students_list
    
    def get_users_for_school(self, token, object_id, top=12, nextlink=''):
        skiptoken = ''
        if nextlink and nextlink.find('skiptoken') != -1:
            link_skiptoken = self._token_re.findall(nextlink)[0]
            skiptoken = '&%s' % link_skiptoken
        users_list = []
        next_link = ''
        try:
            url = 'administrativeUnits/%s/members?api-version=beta&$top=%s%s' % (object_id, top, skiptoken)
            version = ''
            users_content = self.send(url, token, version)
            users_list = users_content['value']
            next_link = users_content.get('odata.nextLink', '')
        except:
            pass
        return users_list, next_link

    def get_students_by_schoolid(self, token, schoolid, top=12, nextlink=''):
        skiptoken = ''
        if nextlink and nextlink.find('skiptoken') != -1:
            link_skiptoken = self._token_re.findall(nextlink)[0]
            skiptoken = '&%s' % link_skiptoken
        students_list = []
        next_link = ''
        try:
            url = "users?api-version=1.5&$filter=extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId eq '%s' and extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType eq 'Student'&$top=%s%s" % (schoolid, top, skiptoken)
            version = ''
            students_content = self.send(url, token, version)
            students_list = students_content['value']
            next_link = students_content.get('odata.nextLink', '')
        except:
            pass
        return students_list, next_link
    
    def get_teachers_by_schoolid(self, token, schoolid, top=12, nextlink=''):
        skiptoken = ''
        if nextlink and nextlink.find('skiptoken') != -1:
            link_skiptoken = self._token_re.findall(nextlink)[0]
            skiptoken = '&%s' % link_skiptoken
        teachers_list = []
        next_link = ''
        try:
            url = "users?api-version=1.5&$filter=extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId eq '%s' and extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType eq 'Teacher'&$top=%s%s" % (schoolid, top, skiptoken)
            version = ''
            teachers_content = self.send(url, token, version)
            teachers_list = teachers_content['value']
            next_link = teachers_content.get('odata.nextLink', '')
        except:
            pass
        return teachers_list, next_link
