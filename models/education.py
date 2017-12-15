'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''

import re
import datetime

class GraphObjectBase(object):

    def __init__(self, prop_dict={}):
        self._prop_dict = prop_dict
        self._custom_data = {}

    def get_value(self, property_name):
         if property_name in self._prop_dict:
            return self._prop_dict[property_name]
         else:
            return ''

    def set_value(self, property_name, value):
        self._prop_dict[property_name] = value
        
    def to_dict(self):
        return dict((name, getattr(self, name)) for name in dir(self) if not name.startswith('_')  and not callable(getattr(self, name)))

    @property
    def id(self):
        return self.get_value('id')
    
    @property
    def custom_data(self):
        return self._custom_data


class School(GraphObjectBase):

    def __init__(self, prop_dict={}):
        super(School, self).__init__(prop_dict)
        self._address = None

    @property
    def external_id (self):
        return self.get_value('externalId')
    
    @property
    def display_name(self):
        return self.get_value('displayName')

    @property
    def principal_name(self):
        return self.get_value('principalName')

    @property
    def highest_grade(self):
        return self.get_value('highestGrade')

    @property
    def number(self):
        return self.get_value('schoolNumber')

    @property
    def lowest_grade(self):
        return self.get_value('lowestGrade')

    @property
    def address(self):
        if not self._address:
            self._address = PhysicalAddress(self.get_value('address'))
        return self._address


class PhysicalAddress(GraphObjectBase):

    def __init__(self, prop_dict={}):
        super(PhysicalAddress, self).__init__(prop_dict)

    @property
    def street(self):
        return self.get_value('street')

    @property
    def city(self):
        return self.get_value('city')

    @property
    def state(self):
        return self.get_value('state')

    @property
    def postal_code(self):
        return self.get_value('postalCode')


class Class(GraphObjectBase):

    def __init__(self, prop_dict={}):
        super(Class, self).__init__(prop_dict)
        self._term = None
        self._members = []
        self._schools = []

    @property
    def display_name(self):
        return self.get_value('displayName')

    @property
    def code(self):
        return self.get_value('classCode')

    @property
    def mail_nickname(self):
        return self.get_value('mailNickname')
    
    @property
    def description(self):
        return self.get_value('description')

    @property
    def term(self):
        if not self._term:
            self._term = Term(self.get_value('term'))
        return self._term

    @property
    def schools(self):
        if not self._schools:
            self._schools = [School(s) for s in self.get_value('schools')]
        return self._schools

    @property
    def members(self):
        if not self._members:
            self._members = [EduUser(m) for m in self.get_value('members')]
        return self._members

    @members.setter
    def members(self, value):
        self._members = value

    @property
    def teachers(self):
        return [m for m in self.members if m.primary_role == 'teacher']

    def is_in_school(self, school_id):
        return any(s for s in self.schools if s.id == school_id)


class Term(GraphObjectBase):

    def __init__(self, prop_dict={}):
        super(Term, self).__init__(prop_dict)

    @property
    def external_id(self):
        return self.get_value('externalId')

    @property
    def display_name(self):
        return self.get_value('displayName')

    @property
    def start_date(self):
        return self.get_value('startDate')

    @property
    def end_date(self):
        return self.get_value('endDate')


class EduUser(GraphObjectBase):

    def __init__(self, prop_dict={}):
        super(EduUser, self).__init__(prop_dict)
        self._schools = []
        self._classes = []
    
    @property
    def display_name(self):
        return self.get_value('displayName')

    @property
    def grade(self):
        return self.get_value('grade')

    @property
    def primary_role(self):
        return self.get_value('primaryRole')

    @property
    def is_teacher(self):
        return self.primary_role == 'teacher'

    @property
    def schools(self):
        if not self._schools:
            self._schools = [School(s) for s in self.get_value('schools')]
        return self._schools

    @property
    def classes(self):
        if not self._classes:
            self._classes = [Class(s) for s in self.get_value('classes')]
        return self._classes

    def is_in_school(self, school_id):
        return any(s for s in self.schools if s.id == school_id)
    
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
    def id(self):
        return self.get_value('id')

    @property
    def mail(self):
        return self.get_value('mail')

    @property
    def topic(self):
        return self.get_value('topic')
