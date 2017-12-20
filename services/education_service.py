'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import re
import constant
from services.rest_api_service import RestApiService
from models.education import School, Class, EduUser,Assignment,AssignmentResource

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

    def get_assignments(self,class_id):
        '''
        Get assignments of a class.
        '''
        url = self.api_base_uri + 'education/classes/' +class_id + "/assignments"     
        return self.rest_api_service.get_object_list(url, self.access_token, model=Assignment)

    def get_assignment(self,class_id,assignment_id):
        url = self.api_base_uri + 'education/classes/' +class_id + "/assignments/"+assignment_id     
        return self.rest_api_service.get_object(url, self.access_token, model=Assignment)

    def add_assignment(self,class_id,name,dueDateTime):
        url = self.api_base_uri + 'education/classes/' +class_id + "/assignments"       
        data={"displayName":name,"status":"draft","dueDateTime":dueDateTime,"allowStudentsToAddResourcesToSubmission":"true","assignTo":{"@odata.type":"#microsoft.graph.educationAssignmentClassRecipient"}}
        return self.rest_api_service.post_json(url,self.access_token,None,data)

    def publish_assignment(self,class_id,assignment_id):
         url = self.api_base_uri + "education/classes/"+class_id+"/assignments/"+assignment_id+"/publish";
         return self.rest_api_service.post_json(url,self.access_token,None,None)

    def getAssignmentResourceFolderURL(self,class_id,assignment_id):
         url = self.api_base_uri + "education/classes/"+class_id+"/assignments/"+assignment_id+"/GetResourcesFolderUrl";
         return self.rest_api_service.get_json(url,self.access_token)

    def getAssignmentResources(self,class_id,assignment_id):
        url = self.api_base_uri + "education/classes/"+class_id+"/assignments/"+assignment_id+"/resources";
        return self.rest_api_service.get_object_list(url, self.access_token, model=AssignmentResource)

    def getAssignmentSubmissionsByUser(self,class_id,assignment_id,user_id):
        url = self.api_base_uri +'education/classes/' +class_id+ '/assignments/'+assignment_id+'/submissions?$filter=submittedBy/user/id eq \''+user_id+'\''
        return self.rest_api_service.get_object_list(url, self.access_token, model=AssignmentResource)
   
    def getSubmissionResources(self,class_id,assignment_id,user_id):
        url = self.api_base_uri +'education/classes/' +class_id+ '/assignments/'+assignment_id+'/submissions?$filter=submittedBy/user/id eq \''+user_id+'\''
        return self.rest_api_service.get_object_list(url, self.access_token, model=AssignmentResource)
    # def uploadFileToOneDrive(self,ids,file):
    #     url = "https://graph.microsoft.com/v1.0/drives/" + ids[0]+"/items/"+ids[1]+":/"+file.name+":/content"
    #     return self.rest_api_service.put_file(url,self.access_token,file)

    def _get_skip_token(self, nextlink):
        if nextlink:
            matches = self.skip_token_re.findall(nextlink)
            if matches:
                return matches[0]
        return ''

    