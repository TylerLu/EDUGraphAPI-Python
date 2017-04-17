"""
schools controller for school info
"""
import re
import datetime
from utils.bingmap_service import BingMapServicer

class SchoolProcesser(object):

    def __init__(self):
        self._bing_map_server = BingMapServicer()
    
    def _assign_school_object_id(self, school):
        return school['objectId']

    def _assign_school_id(self, school):
        id = school['extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId']
        return id

    def _assign_school_name(self, school):
        name = '-'
        if len(school['displayName'].strip()) > 0:
            name = school['displayName']
        return name
    
    def _assign_school_principal_name(self, school):
        principal_name = '-'
        r_principal_name = school.get('extension_fe2174665583431c953114ff7268b7b3_Education_SchoolPrincipalName', '')
        if len(r_principal_name.strip()) > 0:
            principal_name = r_principal_name
        return principal_name
    
    def _assign_lowest_grade(self, school):
        lowest_grade = school.get('extension_fe2174665583431c953114ff7268b7b3_Education_LowestGrade', '')
        return lowest_grade

    def _assign_highest_grade(self, school):
        highest_grade = school.get('extension_fe2174665583431c953114ff7268b7b3_Education_HighestGrade', '')
        return highest_grade
    
    def _assign_address(self, school):
        address = school.get('extension_fe2174665583431c953114ff7268b7b3_Education_Address', '')
        return address

    def _assign_city(self, school):
        city = school.get('extension_fe2174665583431c953114ff7268b7b3_Education_City', '')
        return city

    def _assign_state(self, school):
        state = school.get('extension_fe2174665583431c953114ff7268b7b3_Education_State', '')
        return state

    def _assign_zip(self, school):
        szip = school.get('extension_fe2174665583431c953114ff7268b7b3_Education_Zip', '')
        return szip
    
    def _assign_lat_lon(self, school_dict):
        lat, lon = self._bing_map_server.get_lat_lon(school_dict['state'], school_dict['city'], school_dict['address'])
        school_dict['latitude'] = lat
        school_dict['longitude'] = lon

    def normalize_schools_info(self, schools_list, my_school_id=''):
        '''
        normalize schools info by api result
        '''
        out_schools = []
        temp_schools = []
        for school in schools_list:
            school_dict = {}
            school_dict['object_id'] = self._assign_school_object_id(school)
            school_dict['id'] = self._assign_school_id(school)
            school_dict['name'] = self._assign_school_name(school)
            school_dict['principalname'] = self._assign_school_principal_name(school)
            school_dict['lowestgrade'] = self._assign_lowest_grade(school)
            school_dict['highestgrade'] = self._assign_highest_grade(school)
            school_dict['address'] = self._assign_address(school)
            school_dict['city'] = self._assign_city(school)
            school_dict['state'] = self._assign_state(school)
            school_dict['zip'] = self._assign_zip(school)
            if not school_dict['address'] and not school_dict['zip']:
                school_dict['address'] = '-'
            else:
                self._assign_lat_lon(school_dict)
            if my_school_id and school_dict['id'] == my_school_id:
                out_schools.append(school_dict)
            else:
                temp_schools.append(school_dict)
        temp_schools.sort(key=lambda d:d['name'])
        out_schools.extend(temp_schools)
        return out_schools
    
    def normalize_one_school_info(self, school_result):
        '''
        normalize one school info by api result
        '''
        out_info = {}
        out_info['school_id'] = self._assign_school_id(school_result)
        out_info['school_name'] = self._assign_school_name(school_result)
        out_info['school_principalname'] = self._assign_school_principal_name(school_result)
        out_info['school_lowestgrade'] = self._assign_lowest_grade(school_result)
        out_info['school_highestgrade'] = self._assign_highest_grade(school_result)
        return out_info
    
    def _assign_section_object_id(self, section):
        return section['objectId']

    def _assign_section_name(self, section):
        name = '-'
        if len(section['displayName'].strip()) > 0:
            name = section['displayName']
        return name

    def _assign_combined_course_number(self, section):
        course_name = section['extension_fe2174665583431c953114ff7268b7b3_Education_CourseName']
        course_number = section['extension_fe2174665583431c953114ff7268b7b3_Education_CourseNumber']
        combined_course_number = course_name[0:3].upper() + re.match('\d+', course_number).group()
        return combined_course_number

    def _assign_course_id(self, section):
        course_id = section['extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_CourseId']
        return course_id
    
    def _assign_course_desc(self, section):
        course_desc = section['extension_fe2174665583431c953114ff7268b7b3_Education_CourseDescription']
        return course_desc
    
    def _assign_term_name(self, section):
        term_name = section['extension_fe2174665583431c953114ff7268b7b3_Education_TermName']
        return term_name
    
    def _assign_term_start_date(self, section):
        term_start_date = section['extension_fe2174665583431c953114ff7268b7b3_Education_TermStartDate']
        convert_date = datetime.datetime.strptime(term_start_date, '%m/%d/%Y')
        out_start_date = convert_date.strftime('%Y-%m-%dT%H:%M:%S')
        return out_start_date
        
    def _assign_term_end_date(self, section):
        term_end_date = section['extension_fe2174665583431c953114ff7268b7b3_Education_TermEndDate']
        convert_date = datetime.datetime.strptime(term_end_date, '%m/%d/%Y')
        out_end_date = convert_date.strftime('%Y-%m-%dT%H:%M:%S')
        return out_end_date
    
    def _assign_period(self, section):
        period = section['extension_fe2174665583431c953114ff7268b7b3_Education_Period']
        return period
    
    def _assign_email(self, section):
        email = section['mail']
        return email

    def normalize_sections_info(self, sections_list, my_emails=[]):
        '''
        normalize sections info by api result
        '''
        out_sections = []
        for section in sections_list:
            section_dict = {}
            section_dict['object_id'] = self._assign_section_object_id(section)
            section_dict['name'] = self._assign_section_name(section)
            section_dict['combined_course_number'] = self._assign_combined_course_number(section)
            section_dict['course_id'] = self._assign_course_id(section)
            section_dict['course_desc'] = self._assign_course_desc(section)
            section_dict['term_name'] = self._assign_term_name(section)
            section_dict['term_start_date'] = self._assign_term_start_date(section)
            section_dict['term_end_date'] = self._assign_term_end_date(section)
            section_dict['period'] = self._assign_period(section)
            section_dict['email'] = self._assign_email(section)
            if section_dict['email']  in my_emails:
                section_dict['ismy'] = True
            else:
                section_dict['ismy'] = False
            out_sections.append(section_dict)
        return out_sections
    
    def normalize_mysections_info(self, mysections_list):
        '''
        normalize mysections info by api result
        '''
        my_sections = []
        my_emails = []
        for section in mysections_list:
            section_dict = {}
            section_dict['object_id'] = self._assign_section_object_id(section)
            section_dict['name'] = self._assign_section_name(section)
            section_dict['combined_course_number'] = self._assign_combined_course_number(section)
            section_dict['course_id'] = self._assign_course_id(section)
            section_dict['course_desc'] = self._assign_course_desc(section)
            section_dict['term_name'] = self._assign_term_name(section)
            section_dict['term_start_date'] = self._assign_term_start_date(section)
            section_dict['term_end_date'] = self._assign_term_end_date(section)
            section_dict['period'] = self._assign_period(section)
            section_dict['email'] = self._assign_email(section)
            my_sections.append(section_dict)
            my_emails.append(section_dict['email'])
        my_sections.sort(key=lambda d:d['combined_course_number'])
        return my_sections, my_emails
    
    def _assign_course_name(self, section):
        course_name = section['extension_fe2174665583431c953114ff7268b7b3_Education_CourseName']
        return course_name

    def _assign_course_number(self, section):
        course_number = section['extension_fe2174665583431c953114ff7268b7b3_Education_CourseNumber']
        return course_number

    def _assign_course_desc(self, section):
        course_desc = section['extension_fe2174665583431c953114ff7268b7b3_Education_CourseDescription']
        return course_desc

    def normalize_one_section_info(self, section_result):
        '''
        normalize one section info by api result
        '''
        out_info = {}
        out_info['course_name'] = self._assign_course_name(section_result)
        out_info['course_number'] = self._assign_course_number(section_result)
        out_info['course_displayname'] = self._assign_section_name(section_result)
        out_info['course_desc'] = self._assign_course_desc(section_result)
        out_info['course_period'] = self._assign_period(section_result)
        out_info['course_termname'] = self._assign_term_name(section_result)
        out_info['course_termstartdate'] = self._assign_term_start_date(section_result)
        out_info['course_termenddate'] = self._assign_term_end_date(section_result)
        out_info['email'] = self._assign_email(section_result)
        return out_info

    def _assign_user_object_type(self, user):
        return user['extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType']

    def _assign_user_name(self, user):
        return user['displayName']

    def normalize_teachers_info(self, teachers_list):
        '''
        normalize teachers info by api result
        '''
        out_teachers = []
        for teacher in teachers_list:
            teacher_dict = {}
            teacher_dict['name'] = self._assign_user_name(teacher)
            teacher_dict['photo'] = self._assign_user_photo(teacher)
            out_teachers.append(teacher_dict)
        return out_teachers
    
    def _assign_student_grade(self, student):
        grade = student['extension_fe2174665583431c953114ff7268b7b3_Education_Grade']
        return grade

    def _assign_user_photo(self, user):
        photo = '/Photo/UserPhoto/%s' % user['objectId']
        return photo

    def normalize_students_info(self, students_list):
        '''
        normalize students info by api result
        '''
        out_students = []
        for student in students_list:
            student_dict = {}
            student_dict['uid'] = student['objectId']
            student_dict['name'] = self._assign_user_name(student)
            student_dict['grade'] = self._assign_student_grade(student)
            student_dict['photo'] = self._assign_user_photo(student)
            out_students.append(student_dict)
        return out_students
    
    def _assign_document_web_url(self, document):
        web_url = document.get('webUrl', '')
        return web_url
    
    def _assign_document_name(self, document):
        name = document.get('name', '')
        return name
    
    def _assign_document_last_modified_date_time(self, document):
        last_modified_date_time = document.get('lastModifiedDateTime', '')
        return last_modified_date_time

    def _assign_document_last_modified_user_name(self, document):
        last_modified_user_name = ''
        last_modified_by = document.get('lastModifiedBy', '')
        if last_modified_by:
            last_modified_user_name = last_modified_by['user']['displayName']
        return last_modified_user_name

    def normalize_documents_info(self, documents_list):
        '''
        normalize documents info by api result
        '''
        out_documents = []
        for document in documents_list:
            document_dict = {}
            document_dict['web_url'] = self._assign_document_web_url(document)
            document_dict['name'] = self._assign_document_name(document)
            document_dict['last_modified_date_time'] = self._assign_document_last_modified_date_time(document)
            document_dict['last_modified_user_name'] = self._assign_document_last_modified_user_name(document)
            out_documents.append(document_dict)
        return out_documents
    
    def _assign_conversation_url(self, conversation, email):
        con_id = conversation['id']
        conversation_url = 'https://outlook.office.com/owa/?path=/group/%s/mail&exsvurl=1&ispopout=0&ConvID=%s' % (email, con_id)
        return conversation_url

    def _assign_conversation_topic(self, conversation):
        topic = conversation['topic']
        return topic

    def normalize_conversations_info(self, conversations_list, section_email):
        '''
        normalize conversations info by api result
        '''
        out_conversations = []
        for conversation in conversations_list:
            conversation_dict = {}
            conversation_dict['url'] = self._assign_conversation_url(conversation, section_email)
            conversation_dict['topic'] = self._assign_conversation_topic(conversation)
            out_conversations.append(conversation_dict)
        return out_conversations

    def get_conversations_root(self, section_email):
        '''
        get conversations seeall url
        '''
        seeall_url = 'https://outlook.office.com/owa/?path=/group/%s/mail&exsvurl=1&ispopout=0' % section_email
        return seeall_url
    
    def normalize_users_info(self, users_list):
        '''
        normalize users info by api result
        '''
        out_users = []
        for user in users_list:
            user_dict = {}
            user_dict['object_type'] = self._assign_user_object_type(user)
            user_dict['photo'] = self._assign_user_photo(user)
            user_dict['name'] = self._assign_user_name(user)
            out_users.append(user_dict)
        return out_users

    def prune_next_sections(self, my_sections, all_sections):
        mysections = []
        if my_sections:
            for section in my_sections:
                record = {}
                record['Email'] = section['mail']
                mysections.append(record)

        allsections = []
        if all_sections:
            for section in all_sections:
                record = {}
                record['ObjectId'] = self._assign_section_object_id(section)
                record['DisplayName'] = self._assign_section_name(section)
                record['CombinedCourseNumber'] = self._assign_combined_course_number(section)
                record['CourseId'] = self._assign_course_id(section)
                record['CourseDescription'] = self._assign_course_desc(section)
                record['Members'] = []
                record['TermName'] = self._assign_term_name(section)
                record['TermStartDate'] = self._assign_term_start_date(section)
                record['TermEndDate'] = self._assign_term_end_date(section)
                record['Period'] = self._assign_period(section)
                allsections.append(record)
        return mysections, allsections
    
    def prune_users_info(self, users_list):
        out_users = []
        for user in users_list:
            record = {}
            record['ObjectType'] = self._assign_user_object_type(user)
            record['O365UserId'] = user['objectId']
            record['DisplayName'] = self._assign_user_name(user)
            out_users.append(record)
        return out_users
    
    def prune_students_info(self, students_list):
        out_students = []
        for student in students_list:
            record = {}
            record['ObjectType'] = self._assign_user_object_type(student)
            record['O365UserId'] = student['objectId']
            record['DisplayName'] = self._assign_user_name(student)
            out_students.append(record)
        return out_students
    
    def prune_teachers_info(self, teachers_list):
        out_teachers = []
        for teacher in teachers_list:
            record = {}
            record['ObjectType'] = self._assign_user_object_type(teacher)
            record['O365UserId'] = teacher['objectId']
            record['DisplayName'] = self._assign_user_name(teacher)
            out_teachers.append(record)
        return out_teachers
