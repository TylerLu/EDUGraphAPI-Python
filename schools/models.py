'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
import re
import datetime
from services.bingmap_service import BingMapService

import json
import inspect


class SchoolMap(object):
    def __init__(self):
        self.object_id = 'objectId'
        self.id = 'extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId'
        self.display_name = 'displayName'
        self.principal_name = 'extension_fe2174665583431c953114ff7268b7b3_Education_SchoolPrincipalName'
        self.lowestgrade = 'extension_fe2174665583431c953114ff7268b7b3_Education_LowestGrade'
        self.highestgrade = 'extension_fe2174665583431c953114ff7268b7b3_Education_HighestGrad'
        self.address = 'extension_fe2174665583431c953114ff7268b7b3_Education_Address'
        self.city = 'extension_fe2174665583431c953114ff7268b7b3_Education_City'
        self.state = 'extension_fe2174665583431c953114ff7268b7b3_Education_State'
        self.zip = 'extension_fe2174665583431c953114ff7268b7b3_Education_Zip'
        self.latitude = ''
        self.longitude = ''

class ClassMap(object):
    def __init__(self):
        self.object_id = 'objectId'
        self.ObjectId = 'objectId'
        self.id = 'extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId'
        self.display_name = 'displayName'
        self.mail = 'mail'
        self.course_id = 'extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_CourseId'
        self.CourseId = 'extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_CourseId'
        self.course_desc = 'extension_fe2174665583431c953114ff7268b7b3_Education_CourseDescription'
        self.CourseDescription = 'extension_fe2174665583431c953114ff7268b7b3_Education_CourseDescription'
        self.course_name = 'extension_fe2174665583431c953114ff7268b7b3_Education_CourseName'
        self.course_number = 'extension_fe2174665583431c953114ff7268b7b3_Education_CourseNumber'
        self.term_name = 'extension_fe2174665583431c953114ff7268b7b3_Education_TermName'
        self.TermName = 'extension_fe2174665583431c953114ff7268b7b3_Education_TermName'
        self.course_termname = 'extension_fe2174665583431c953114ff7268b7b3_Education_TermName'
        self.term_start_date = 'extension_fe2174665583431c953114ff7268b7b3_Education_TermStartDate'
        self.term_end_date = 'extension_fe2174665583431c953114ff7268b7b3_Education_TermEndDate'
        self.period = 'extension_fe2174665583431c953114ff7268b7b3_Education_Period'
        self.Period = 'extension_fe2174665583431c953114ff7268b7b3_Education_Period'
        self.course_period = 'extension_fe2174665583431c953114ff7268b7b3_Education_Period'
        self.email = 'mail'

class UserMap(object):
    def __init__(self):
        self.object_type = 'extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType'
        self.ObjectType = 'extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType'
        self.object_id = 'objectId'
        self.O365UserId = 'objectId'
        self.uid = 'objectId'
        self.name = 'displayName'
        self.display_name = 'displayName'
        self.DisplayName = 'displayName'
        self.grade = 'extension_fe2174665583431c953114ff7268b7b3_Education_Grade'

unserialize_map = {
    'school': SchoolMap,
    'class': ClassMap,
    'user': UserMap
}

def unserialize_object(d):
    clsname = d.pop('__classname__', None)
    if clsname:
        cls = unserialize_map[clsname]
        obj = cls()
        out_dict = {}
        out_keys = obj.__dict__.keys()
        for key in out_keys:
            d_key = getattr(obj, key, '')
            if d_key:
                value = d.get(d_key, '')
            else:
                value = ''
            out_dict[key] = value
        return out_dict
    else:
        return d

def json_convert(data, name):
    data['__classname__'] = name
    new_data = json.dumps(data)
    convert_dict = json.loads(new_data, object_hook=unserialize_object)
    return convert_dict

class School(object):

    def __init__(self, data):
        self._data = data
        self._bing_map_server = BingMapService()

    def _assign_name(self, display_name):
        name = '-'
        if len(display_name.strip()) > 0:
            name = display_name
        return name
    
    def _assign_principal_name(self, principal_name):
        p_name = '-'
        if len(principal_name.strip()) > 0:
            p_name = principal_name
        return p_name
    
    def _assign_lat_lon(self, school_dict):
        lat, lon = self._bing_map_server.get_lat_lon(school_dict['state'], school_dict['city'], school_dict['address'])
        school_dict['latitude'] = lat
        school_dict['longitude'] = lon

    def convert(self):
        school_dict = json_convert(self._data, 'school')
        school_dict['name'] = self._assign_name(school_dict['display_name'])
        school_dict['principalname'] = self._assign_principal_name(school_dict['principal_name'])
        if not school_dict['address'] and not school_dict['zip']:
            school_dict['address'] = '-'
        else:
            self._assign_lat_lon(school_dict)
        return school_dict

class ClassModel(object):
    def __init__(self, data):
        self._data = data

    def _assign_name(self, display_name):
        name = '-'
        if len(display_name.strip()) > 0:
            name = display_name
        return name

    def _assign_combined_course_number(self, course_name, course_number):
        combined_course_number = course_name[0:3].upper() + re.match('\d+', course_number).group()
        return combined_course_number

    def _assign_term_start_date(self, term_start_date):
        convert_date = datetime.datetime.strptime(term_start_date, '%m/%d/%Y')
        out_start_date = convert_date.strftime('%Y-%m-%dT%H:%M:%S')
        return out_start_date
        
    def _assign_term_end_date(self, term_end_date):
        convert_date = datetime.datetime.strptime(term_end_date, '%m/%d/%Y')
        out_end_date = convert_date.strftime('%Y-%m-%dT%H:%M:%S')
        return out_end_date
    
    def convert(self):
        class_dict = json_convert(self._data, 'class')
        class_dict['name'] = self._assign_name(class_dict['display_name'])
        class_dict['course_displayname'] = class_dict['name']
        class_dict['DisplayName'] = class_dict['name']
        class_dict['combined_course_number'] = self._assign_combined_course_number(class_dict['course_name'], class_dict['course_number'])
        class_dict['CombinedCourseNumber'] = class_dict['combined_course_number']
        class_dict['term_start_date'] = self._assign_term_start_date(class_dict['term_start_date'])
        class_dict['course_termstartdate'] = class_dict['term_start_date']
        class_dict['TermStartDate'] = class_dict['term_start_date']
        class_dict['term_end_date'] = self._assign_term_end_date(class_dict['term_end_date'])
        class_dict['course_termenddate'] = class_dict['term_end_date']
        class_dict['TermEndDate'] = class_dict['term_end_date']
        class_dict['Members'] = []
        return class_dict

class User(object):
    def __init__(self, data):
        self._data = data
        
    def convert(self):
        user_dict = json_convert(self._data, 'user')
        user_dict['photo'] = '/Photo/UserPhoto/%s' % user_dict['object_id']
        return user_dict
    
class Document(object):
    def __init__(self, data):
        self._data = data
    
    def _assign_document_last_modified_user_name(self):
        last_modified_user_name = ''
        last_modified_by = self._data.get('lastModifiedBy', '')
        if last_modified_by:
            last_modified_user_name = last_modified_by['user']['displayName']
        return last_modified_user_name

    def convert(self):
        document_dict = {}
        document_dict['web_url'] = self._data.get('webUrl', '')
        document_dict['name'] = self._data.get('name', '')
        document_dict['last_modified_date_time'] = self._data.get('lastModifiedDateTime', '')
        document_dict['last_modified_user_name'] = self._assign_document_last_modified_user_name()
        return document_dict

class Conversation(object):
    def __init__(self, data, mail):
        self._data = data
        self._mail = mail
    
    def _assign_conversation_url(self):
        con_id = self._data['id']
        conversation_url = 'https://outlook.office.com/owa/?path=/group/%s/mail&exsvurl=1&ispopout=0&ConvID=%s' % (self._mail, con_id)
        return conversation_url

    def convert(self):
        conversation_dict = {}
        conversation_dict['url'] = self._assign_conversation_url()
        conversation_dict['topic'] = self._data['topic']
        return conversation_dict

