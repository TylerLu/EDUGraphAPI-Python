'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
from constant import Roles
from constant import O365ProductLicenses

from services.ms_api_service import MSGraphRequest
from services.aad_api_service import AADGraphRequest

from schools.models import School, ClassModel, User, Document, Conversation

class SchoolService(object):

    def __init__(self):
        self._aad_request = AADGraphRequest()
        self._ms_request = MSGraphRequest()
    
    def _normalize_schools_info(self, schools_list, my_school_id=''):
        '''
        normalize schools info by api result
        '''
        out_schools = []
        temp_schools = []
        for data in schools_list:
            school_obj = School(data)
            school_dict = school_obj.convert()
            if my_school_id and school_dict['id'] == my_school_id:
                out_schools.append(school_dict)
            else:
                temp_schools.append(school_dict)
        temp_schools.sort(key=lambda d:d['name'])
        out_schools.extend(temp_schools)
        return out_schools
    
    def _normalize_class_school_info(self, data):
        '''
        normalize one school info by api result
        '''
        school_obj = School(data)
        out_info = school_obj.convert()
        return out_info
    
    def _normalize_class_detail_info(self, data):
        '''
        normalize one class info by api result
        '''
        class_obj = ClassModel(data)
        out_info = class_obj.convert()
        return out_info

    def _normalize_classes_info(self, classes_list, my_emails=[]):
        '''
        normalize classes info by api result
        '''
        out_classes = []
        for data in classes_list:
            class_obj = ClassModel(data)
            class_dict = class_obj.convert()
            if class_dict['email']  in my_emails:
                class_dict['ismy'] = True
            else:
                class_dict['ismy'] = False
            out_classes.append(class_dict)
        return out_classes
    
    def _normalize_my_classes_info(self, classes_list):
        '''
        normalize my classes info by api result
        '''
        out_classes = []
        user_class_emails = []
        for data in classes_list:
            class_obj = ClassModel(data)
            class_dict = class_obj.convert()
            out_classes.append(class_dict)
            user_class_emails.append(class_dict['email'])
        out_classes.sort(key=lambda d:d['combined_course_number'])
        return out_classes, user_class_emails
    
    def _normalize_teachers_info(self, teachers_list):
        '''
        normalize teachers info by api result
        '''
        out_teachers = []
        for data in teachers_list:
            teacher_obj = User(data)
            teacher_dict = teacher_obj.convert()
            out_teachers.append(teacher_dict)
        return out_teachers
    
    def _normalize_students_info(self, students_list):
        '''
        normalize students info by api result
        '''
        out_students = []
        for data in students_list:
            student_obj = User(data)
            student_dict = student_obj.convert()
            out_students.append(student_dict)
        return out_students
    
    def _normalize_documents_info(self, documents_list):
        '''
        normalize documents info by api result
        '''
        out_documents = []
        for data in documents_list:
            document_obj = Document(data)
            document_dict = document_obj.convert()
            out_documents.append(document_dict)
        return out_documents
    
    def _normalize_conversations_info(self, conversations_list, section_email):
        '''
        normalize conversations info by api result
        '''
        out_conversations = []
        for data in conversations_list:
            conver_obj = Conversation(data, section_email)
            conversation_dict = conver_obj.convert()
            out_conversations.append(conversation_dict)
        return out_conversations
    
    def _normalize_users_info(self, users_list):
        '''
        normalize users info by api result
        '''
        out_users = []
        for data in users_list:
            user_obj = User(data)
            user_dict = user_obj.convert()
            out_users.append(user_dict)
        return out_users

    def _prune_next_classes(self, my_classes, all_classes):
        mysections = []
        if my_classes:
            for section in my_classes:
                record = {}
                record['Email'] = section['email']
                mysections.append(record)

        allsections = []
        if all_classes:
            for data in all_classes:
                class_obj = ClassModel(data)
                record = class_obj.convert()
                allsections.append(record)
        return mysections, allsections
    
    def _prune_users_info(self, users_list):
        out_users = []
        for data in users_list:
            user_obj = User(data)
            record = user_obj.convert()
            out_users.append(record)
        return out_users
    
    def get_user_schools(self, school_user_id):
        all_schools = self._aad_request.get_all_schools()
        user_schools = self._normalize_schools_info(all_schools, school_user_id)
        return user_schools

    def get_class_school(self, school_object_id):
        school = self._aad_request.get_one_school(school_object_id)
        school_info = self._normalize_class_school_info(school)
        return school_info
    
    def get_user_classes(self, school_user_id):
        classes = self._aad_request.get_section_by_member(school_user_id)
        out_classes, user_class_emails = self._normalize_my_classes_info(classes)
        return out_classes, user_class_emails

    def get_school_classes(self, school_user_id, my_emails=[]):
        all_classes, sectionsnextlink = self._aad_request.get_sections_by_schoolid(school_user_id)
        out_classes = self._normalize_classes_info(all_classes, my_emails)
        return out_classes, sectionsnextlink

    def get_current_class(self, class_object_id):
        one_section = self._aad_request.get_one_section(class_object_id)
        section_info = self._normalize_class_detail_info(one_section)
        return section_info

    def get_next_classes(self, school_user_id, nextlink, my_classes):
        all_classes, sectionsnextlink = self._aad_request.get_sections_by_schoolid(school_user_id, nextlink=nextlink)
        mysections, nextsections = self._prune_next_classes(my_classes, all_classes)
        return mysections, nextsections
    
    def get_class_teachers(self, class_object_id):
        all_teachers = self._aad_request.get_teachers_for_section(class_object_id)
        out_teachers = self._normalize_teachers_info(all_teachers)
        return out_teachers

    def get_class_students(self, class_object_id):
        all_students = self._aad_request.get_students_for_section(class_object_id)
        out_students = self._normalize_students_info(all_students)
        return out_students
    
    def get_documents(self, class_object_id):
        all_documents = self._ms_request.get_documents_for_section(class_object_id)
        out_documents = self._normalize_documents_info(all_documents)
        return out_documents
    
    def get_documents_root(self, class_object_id):
        documents_root = self._ms_request.get_documents_root(class_object_id)
        return documents_root
        
    def get_conversations(self, class_object_id, section_mail):
        all_conversations = self._ms_request.get_conversatoins_for_section(class_object_id)
        out_conversations = self._normalize_conversations_info(all_conversations, section_mail)
        return out_conversations
    
    def get_conversations_root(self, section_email):
        seeall_url = 'https://outlook.office.com/owa/?path=/group/%s/mail&exsvurl=1&ispopout=0' % section_email
        return seeall_url
    
    def get_current_users(self, school_object_id):
        all_users, usersnextlink = self._aad_request.get_users_for_school(school_object_id)
        out_users = self._normalize_users_info(all_users)
        return out_users, usersnextlink

    def get_current_teachers(self, school_user_id):
        all_teachers, teachersnextlink = self._aad_request.get_teachers_by_schoolid(school_user_id)
        out_teachers = self._normalize_teachers_info(all_teachers)
        return out_teachers, teachersnextlink

    def get_current_students(self, school_user_id):
        all_students, studentsnextlink = self._aad_request.get_students_by_schoolid(school_user_id)
        out_students = self._normalize_students_info(all_students)
        return out_students, studentsnextlink

    def get_next_users(self, school_object_id, nextlink):
        all_users, usersnextlink = self._aad_request.get_users_for_school(school_object_id, nextlink=nextlink)
        out_users = self._prune_users_info(all_users)
        return out_users, usersnextlink
    
    def get_next_teachers(self, school_user_id, nextlink):
        all_teachers, teachersnextlink = self._aad_request.get_teachers_by_schoolid(school_user_id, nextlink=nextlink)
        out_teachers = self._prune_users_info(all_teachers)
        return out_teachers, teachersnextlink
    
    def get_next_students(self, school_user_id, nextlink):
        all_students, studentsnextlink = self._aad_request.get_students_by_schoolid(school_user_id, nextlink=nextlink)
        out_students = self._prune_users_info(all_students)
        return out_students, studentsnextlink
    
    def get_user_groups(self, school_user_id):
        my_sections = self._aad_request.get_section_by_member(school_user_id)
        groups = []
        for section in my_sections:
            groups.append(section['displayName'])
        return groups

class O365UserService(object):

    def __init__(self):
        self._aad_request = AADGraphRequest()
        self._ms_request = MSGraphRequest()

    def _check_admin(self, role):
        if role == 'Admin':
            return True
        return False
    
    def _check_role(self, uid, admin_ids, sku_ids):
        roles = []
        role = ''
        if uid in admin_ids:
            roles.append('Admin')
        else:
            for sid in sku_ids:
                if sid == O365ProductLicenses.Faculty or sid == O365ProductLicenses.FacultyPro:
                    roles.append(Roles.Faculty)
                if sid == O365ProductLicenses.Student or sid == O365ProductLicenses.StudentPro:
                    roles.append(Roles.Student)
        if roles:
            if 'Admin' in roles:
                role = 'Admin'
            elif 'Faculty' in roles:
                role = 'Teacher'
            elif 'Student' in roles:
                role = 'Student'
        return role
    
    def _check_student(self, role):
        if role == 'Student':
            return True
        return False

    def _assign_full_name(self, user_dict):
        given_name = user_dict['givenName'].strip()
        sur_name = user_dict['surname'].strip()
        if given_name and sur_name:
            full_name = given_name + ' ' + sur_name
        else:
            full_name = user_dict['displayName']
        return full_name
    
    def _assign_photo(self, uid):
        photo = '/Photo/UserPhoto/%s' % uid
        return photo
    
    def _assign_mail(self, user_dict):
        mail = ''
        if not user_dict['mail']:
            mail = user_dict['userPrincipalName']
        else:
            mail = user_dict['mail']
        return mail

    def _normalize_base_user_info(self, client, extra_info, admin_ids=None):
        '''
        normalize sign in user info from MS Graph client
        '''
        user_obj = client.me.get()
        user_dict = user_obj.to_dict()
        user_info = {}
        user_info['isauthenticated'] = True
        user_info['uid'] = user_dict['id']
        user_info['mail'] = self._assign_mail(user_dict)
        user_info['photo'] = '/Photo/UserPhoto/%s' % user_dict['id']
        user_info['display_name'] = self._assign_full_name(user_dict)
        user_info['first_name'] = user_dict['givenName']
        user_info['last_name'] = user_dict['surname']
        user_info['role'] = self._check_role(user_dict['id'], admin_ids, extra_info.get('sku_ids'))
        user_info['isadmin'] = self._check_admin(user_info['role'])
        user_info['isstudent'] = self._check_student(user_info['role'])
        user_info['school_uid'] = extra_info.get('school_uid')
        user_info['school_id'] = extra_info.get('school_id')
        return user_info

    def get_current_user(self):
        admin_ids = self._aad_request.get_admin_ids()
        extra_info = self._aad_request.get_user_extra_info()
        ms_client = self._ms_request.get_client()
        user = self._normalize_base_user_info(ms_client, extra_info, admin_ids)
        return user

    def get_photo(self, user_object_id):
        photo = self._ms_request.get_user_photo(user_object_id)
        return photo
