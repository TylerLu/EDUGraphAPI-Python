'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
import re
import datetime
from services.bingmap_service import BingMapService

class GraphObjectBase(object):

    def __init__(self, prop_dict={}):
        self._prop_dict = prop_dict

    def get_value(self, property_name):
         if property_name in self._prop_dict:
            return self._prop_dict[property_name]
         else:
            return ''

class School(GraphObjectBase):
    def __init__(self, prop_dict={}):
        self._bing_map_server = BingMapService()
        super(School, self).__init__(prop_dict)
        self._lat, self._lon = self._get_lat_lon()

    @property
    def object_id(self):
        return self.get_value('objectId')

    @property
    def id(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId')
    
    @property
    def name(self):
        name = self.get_value('displayName')
        if not name or len(name.strip()) == 0:
            name = '-'
        return name

    @property
    def display_name(self):
        return self.get_value('displayName')

    @property
    def principal_name(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_SchoolPrincipalName')
    
    @property
    def principalname(self):
        p_name = self.principal_name
        if not p_name or len(p_name.strip()) == 0:
            p_name = '-'
        return p_name

    @property
    def lowestgrade(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_LowestGrade')

    @property
    def highestgrade(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_HighestGrade')

    @property
    def zip(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_Zip')

    @property
    def address(self):
        address = self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_Address')
        zip = self.zip
        if not address and not zip:
            address = '-'
        return address

    @property
    def city(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_City')

    @property
    def state(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_State')

    @property
    def latitude(self):
        return self._lat

    @property
    def longitude(self):
        return self._lon

    def _get_lat_lon(self):
        state = self.state
        city = self.city
        address = self.address
        zip = self.zip
        if address or zip:
            lat, lon = self._bing_map_server.get_lat_lon(state, city, address)
            return lat, lon
        else:
            return None, None

class Section(GraphObjectBase):
    def __init__(self, prop_dict={}):
        super(Section, self).__init__(prop_dict)

    @property
    def object_id(self):
        return self.get_value('objectId')
    
    @property
    def ObjectId(self):
        return self.object_id
        
    @property
    def id(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId')
    
    @property
    def mail(self):
        return self.get_value('mail')

    @property
    def email(self):
        return self.mail
    
    @property
    def Email(self):
        return self.mail

    @property
    def display_name(self):
        return self.get_value('displayName')

    @property
    def name(self):
        name = self.get_value('displayName')
        if not name or len(name.strip()) == 0:
            name = '-'
        return name

    @property
    def course_displayname(self):
        return self.name

    @property
    def DisplayName(self):
        return self.name

    @property
    def course_id(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_CourseId')
    
    @property
    def CourseId(self):
        return self.course_id
    
    @property
    def course_desc(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_CourseDescription')

    @property
    def CourseDescription(self):
        return self.course_desc
    
    @property
    def course_name(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_CourseName')
    
    @property
    def course_number(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_CourseNumber')
    
    @property
    def term_name(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_TermName')

    @property
    def TermName(self):
        return self.term_name
    
    @property
    def course_termname(self):
        return self.term_name

    @property
    def start_date(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_TermStartDate')

    @property
    def end_date(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_TermEndDate')

    @property
    def period(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_Period')

    @property
    def Period(self):
        return self.period

    @property
    def course_period(self):
        return self.period

    @property
    def ObjectType(self):
        return self.get_value('ObjectType')

    @property
    def EducationObjectType(self):
        return self.get_value('EducationObjectType')

    @property
    def school_id(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId')

    @property
    def combined_course_number(self):
        combined_course_number = ''
        if self.course_name and self.course_number:
            combined_course_number = self.course_name[0:3].upper() + re.match('\d+', self.course_number).group()
        return combined_course_number

    @property
    def CombinedCourseNumber(self):
        return self.combined_course_number

    @property
    def term_start_date(self):
        out_start_date = ''
        if self.start_date:
            convert_date = datetime.datetime.strptime(self.start_date, '%m/%d/%Y')
            out_start_date = convert_date.strftime('%Y-%m-%dT%H:%M:%S')
        return out_start_date

    @property
    def course_termstartdate(self):
        return self.term_start_date

    @property
    def TermStartDate(self):
        return self.term_start_date

    @property
    def term_end_date(self):
        out_end_date = ''
        if self.end_date:
            convert_date = datetime.datetime.strptime(self.end_date, '%m/%d/%Y')
            out_end_date = convert_date.strftime('%Y-%m-%dT%H:%M:%S')
        return out_end_date
    
    @property
    def course_termenddate(self):
        return self.term_end_date

    @property
    def TermEndDate(self):
        return self.term_end_date

    @property
    def Members(self):
        return []

class EduUser(GraphObjectBase):
    def __init__(self, prop_dict={}):
        super(EduUser, self).__init__(prop_dict)

    @property
    def object_type(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType')

    @property
    def ObjectType(self):
        return self.object_type
    
    @property
    def uid(self):
        return self.get_value('objectId')

    @property
    def object_id(self):
        return self.uid

    @property
    def O365UserId(self):
        return self.uid

    @property
    def name(self):
        return self.get_value('displayName')

    @property
    def display_name(self):
        return self.name

    @property
    def DisplayName(self):
        return self.name

    @property
    def grade(self):
        return self.get_value('extension_fe2174665583431c953114ff7268b7b3_Education_Grade')

    @property
    def photo(self):
        photo = '/Photo/UserPhoto/%s' % self.uid
        return photo

class Document(GraphObjectBase):
    def __init__(self, prop_dict={}):
        super(Document, self).__init__(prop_dict)

    @property
    def web_url(self):
        return self.get_value('webUrl')
    
    @property
    def name(self):
        return self.get_value('name')
    
    @property
    def last_modified_date_time(self):
        return self.get_value('lastModifiedDateTime')

    @property
    def last_modified_user_name(self):
        last_modified_user_name = ''
        last_modified_by = self.get_value('lastModifiedBy')
        if last_modified_by:
            last_modified_user_name = last_modified_by['user']['displayName']
        return last_modified_user_name

class Conversation(GraphObjectBase):
    def __init__(self, prop_dict={}):
        super(Conversation, self).__init__(prop_dict)

    @property
    def mail(self):
        return self.get_value('mail')

    @property
    def topic(self):
        return self.get_value('topic')
    
    @property
    def url(self):
        cid = self.get_value('id')
        url = 'https://outlook.office.com/owa/?path=/group/%s/mail&exsvurl=1&ispopout=0&ConvID=' + cid
        return url
