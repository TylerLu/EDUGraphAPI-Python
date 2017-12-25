'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import json
import constant
from utils.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from decorator import login_required, linked_users_only

from services.token_service import TokenService
from services.auth_service import AuthService
from services.ms_graph_service import MSGraphService
from services.education_service import EducationService
from services.user_service import UserService
from datetime import datetime
import time
from django import forms


user_service = UserService()
token_service = TokenService()

@login_required
@linked_users_only
def schools(request):   
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)

    education_service = EducationService(user.tenant_id, token)
    me = education_service.get_me()

    schools = education_service.get_schools()
    for school in schools:
        school.custom_data['is_my'] = me.is_in_school(school.id)

    # sort schools: my school will be put to the top
    schools.sort(key=lambda s:s.display_name if me.is_in_school(s.id) else 'Z_' + s.display_name)
  
    context = {
        'user': user,
        'me': me,
        'schools': schools
    }
    return render(request, 'schools/index.html', context)

@login_required
@linked_users_only
def classes(request, school_id):
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)

    education_service = EducationService(user.tenant_id, token)
    school = education_service.get_school(school_id)
    my_classes = education_service.get_my_classes(school_id)
    all_classes, classesnextlink = education_service.get_classes(school_id, 12)

    for c in all_classes:
        my_class = next((mc for mc in my_classes if c.id == mc.id), None)
        c.custom_data['is_my'] = my_class != None
        if my_class != None:
            c.members = my_class.members

    context = {
        'user': user,
        'school': school,
        'classesnextlink': classesnextlink,
        'classes': all_classes,
        'myclasses': my_classes,
        'school_id': school_id,
        'is_in_a_school': True
    }
    return render(request, 'schools/classes.html', context)

@login_required
def classes_next(request, school_id):
    nextlink = request.GET.get('nextLink')
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)

    education_service = EducationService(user.tenant_id, token)
    #school = education_service.get_school(school_id)
    my_classes = education_service.get_my_classes(school_id)
    all_classes, classnextlink = education_service.get_classes(school_id, top=12, nextlink=nextlink)

    for c in all_classes:
        my_class = next((mc for mc in my_classes if c.id == mc.id), None)
        c.custom_data['is_my'] = my_class != None
        if my_class != None:
            c.members = my_class.members

    # my_section_list = [m.to_dict() for m in my_classes]

    ajax_result = {}
    ajax_result['classes'] = {}
    ajax_result['classes']['value'] = [{
          'is_my': c.custom_data['is_my'],
          'display_name': c.display_name,
          'code': c.code,
          'teachers': [{ 'display_name': t.display_name } for t in c.teachers],
          'term_name': c.term.display_name,
          'term_start_time': c.term.start_date,
          'term_end_time': c.term.end_date } for c in all_classes]
    ajax_result['classes']['next_link'] = classnextlink
    # ajax_result['MyClasss'] = my_section_list

    return JsonResponse(ajax_result, safe=False)

@login_required
@linked_users_only
def add_coteacher(request, class_id, user_object_id):    
    previousURL = request.META.get('HTTP_REFERER')    
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)
    education_service = EducationService(user.tenant_id, token)
    education_service.add_member(class_id,user_object_id)
    education_service.add_owner(class_id,user_object_id)
    return HttpResponseRedirect(previousURL)

@login_required
@linked_users_only
def class_details(request, school_id, class_id):
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)
    education_service = EducationService(user.tenant_id, token)
    me = education_service.get_me()

    token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)
    education_service = EducationService(user.tenant_id, token)

    school = education_service.get_school(school_id)
    current_class = education_service.get_class(class_id)    
    members = education_service.get_class_members(class_id)
    teachers = [m for m in members if m.primary_role == 'teacher']
    students = [m for m in members if m.primary_role == 'student']    
    
    # set favorite colors and seating positions
    for student in students:
        favorite_color = user_service.get_favorite_color_by_o365_user_id(student.id)
        if favorite_color:
            student.custom_data['favorite_color'] = favorite_color
        seating_position = user_service.get_seating_position(student.id, class_id)
        if not seating_position:
            seating_position = 0
        student.custom_data['position'] = seating_position
   
    assignments = education_service.get_assignments(class_id)
    for assignment in assignments: 
        if assignment.dueDateTime !=None:      
            assignment.dueDateTimeLocal = datetime_from_utc_to_local(datetime.strptime(assignment.dueDateTime, '%Y-%m-%dT%H:%M:%SZ')).strftime("%m/%d/%Y")



    all_teachers = education_service.get_teachers(school.number)
    filtered_teachers = [t for t in all_teachers if all(t.id != i.id for i in teachers)]

    # set seatrange
    seatrange = range(1, 37)

    ms_token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)
    ms_graph_service = MSGraphService(ms_token)

    documents = ms_graph_service.get_documents(class_id)
    documents_root = ms_graph_service.get_documents_root(class_id)
    conversations = ms_graph_service.get_conversations(class_id)
    for conversation in conversations:
        conversation.custom_data['url'] = ms_graph_service.get_conversations_url(conversation.id, current_class.mail_nickname)
    conversations_root = ms_graph_service.get_conversations_root(current_class.mail_nickname)

    favorite_color = user_service.get_favorite_color_by_o365_user_id(user.o365_user_id)

    context = {
        'user': user,
        'is_student':me.is_student,
        'school': school,
        'class': current_class,
        'teachers': teachers,
        'students': students,
        'documents': documents,
        'documents_root': documents_root,
        'conversations': conversations,
        'conversations_root': conversations_root,
        'seatrange': seatrange,
        'school_id': school_id,
        'class_id': class_id,
        'is_in_a_school': True,
        'favorite_color': favorite_color,
        'filtered_teachers': filtered_teachers,
        'assignments' : assignments
    }
    return render(request, 'schools/classdetails.html', context)

@login_required
def save_seating_arrangements(request):
    if request.is_ajax() and request.method == 'POST':
        seat_arrangements = json.loads(request.body.decode())
        user_service.update_positions(seat_arrangements)
    return HttpResponse(json.dumps({'save':'ok'}))

@login_required
def new_assignment(request):
    if request.method == 'POST':        
        post=request.POST        
        user = AuthService.get_current_user(request)
        token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)
        education_service = EducationService(user.tenant_id, token)
        dueDate = post["duedate"] + "T" + post["duetime"] + "Z"       
        dueDateUTC=datetime.strptime(dueDate,"%m/%d/%YT%H:%M %pZ").strftime("%Y-%m-%dT%H:%M:%SZ")
        result = education_service.add_assignment(post["classId"],post["name"],dueDateUTC)
        assignment = json.loads(result.content)
        if post['status']=="assigned":
           education_service.publish_assignment(post["classId"],assignment["id"])


        files= request.FILES.getlist("fileUpload")
        if files !=None:
            resourceFolderURL = education_service.get_Assignment_Resource_Folder_URL(post["classId"],assignment["id"])["value"]
            ids = getIds(resourceFolderURL)
            
            for file in files:
               driveFile = uploadFileToOneDrive(resourceFolderURL,file,education_service)      
               resourceUrl = "https://graph.microsoft.com/v1.0/drives/" + ids[0] + "/items/" + driveFile["id"]
               education_service.add_assignment_resources(post["classId"],assignment["id"],driveFile["name"],resourceUrl)
    
        
        referer = request.META.get('HTTP_REFERER') 
        if referer.find("?")==-1:
            referer +="?tab=assignments"
        return HttpResponseRedirect(referer)

@login_required
def get_assignment_resources(request,class_id,assignment_id):
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)
    education_service = EducationService(user.tenant_id, token)
    resources = education_service.get_Assignment_Resources(class_id,assignment_id)   
    result=[]
    for resource in resources:
        resourceArray={} 
        resourceArray["id"]=resource.id
        resourceArray["resource"]=resource.resource["displayName"]
        result.append(resourceArray)

    return JsonResponse(result, safe=False)

@login_required
def get_assignment_submission_resources(request,class_id,assignment_id):
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)
    education_service = EducationService(user.tenant_id, token)
    assignemtnResources = education_service.get_Assignment_Resources(class_id,assignment_id)
    submissionResources = education_service.get_Assignment_Submissions_By_User(class_id,assignment_id,user.o365_user_id)
    
    result={}
    resourceArray=[] 
    submissionResourcesArray=[]
    for resource in assignemtnResources:
        obj={}
        obj["id"]=resource.id
        obj["resource"]=resource.resource["displayName"]
        resourceArray.append(obj)
    result["resources"]=resourceArray;
    
    result["submissionId"]=submissionResources[0].id
    for resource in submissionResources:
       for item in resource.resources:
           obj={}
           obj["id"]=item["id"]
           obj["resource"]=item["resource"]["displayName"]
           submissionResourcesArray.append(obj)
    result["submissionResources"]=submissionResourcesArray;
           
    return JsonResponse(result, safe=False)

@login_required
def get_submissions(request,class_id,assignment_id):
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)
    education_service = EducationService(user.tenant_id, token)  
    submissions = education_service.get_Submissions(class_id,assignment_id)   
    ms_graph_service = MSGraphService(token)

    result=[]
    for submission in submissions:
        userId =  submission.submittedBy["user"]["id"];
        user = ms_graph_service.get_user_info(userId)                
        resources= education_service.get_Submission_Resources(class_id,assignment_id,submission.id)
        array={}
        array["displayName"]=user["displayName"]
        array["submittedDateTime"]  = submission.submittedDateTime 
        
        resources_array=[]
        for resource in resources:
            resources_dict={}
            resources_dict["displayName"] = resource.resource["displayName"]
            resources_array.append(resources_dict)
        array["resources"]=  resources_array  
        result.append(array)

    return JsonResponse(result, safe=False)
        

@login_required
def update_assignment(request):
   if request.method == 'POST':
  
        post=request.POST
        files=request.FILES
        user = AuthService.get_current_user(request)
        token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)
        education_service = EducationService(user.tenant_id, token)  
        assignment = education_service.get_assignment(post["classId"],post["assignmentId"])  

        if assignment.status=='draft' and post['assignmentStatus']=='assigned':
            education_service.publish_assignment(post['classId'], post['assignmentId'])
        
       
        files= request.FILES.getlist("newResource")

        if files !=None:
            resourceFolderURL = education_service.get_Assignment_Resource_Folder_URL(post["classId"],post["assignmentId"])["value"]
            ids = getIds(resourceFolderURL)
            for file in files:
               driveFile = uploadFileToOneDrive(resourceFolderURL,file,education_service)      
               resourceUrl = "https://graph.microsoft.com/v1.0/drives/" + ids[0] + "/items/" + driveFile["id"]
               education_service.add_assignment_resources(post["classId"],post["assignmentId"],driveFile["name"],resourceUrl)
    
        referer = request.META.get('HTTP_REFERER') 
        if referer.find("?")==-1:
            referer +="?tab=assignments"
        return HttpResponseRedirect(referer)

@login_required
def newAssignmentSubmissionResource(request):
    if request.method == 'POST':
        files= request.FILES.getlist("newResource")
        if len(files)!=0:
            post=request.POST            
            user = AuthService.get_current_user(request)
            token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)
            education_service = EducationService(user.tenant_id, token)  
            submissions = education_service.get_Assignment_Submissions_By_User(post["classId"],post["assignmentId"],user.o365_user_id)  
            if len(submissions)!=0:
                resourceFolderURL = submissions[0].resourcesFolderUrl
                ids = getIds(resourceFolderURL)
                for file in files:
                    driveFile = uploadFileToOneDrive(resourceFolderURL,file,education_service)      
                    resourceUrl = "https://graph.microsoft.com/v1.0/drives/" + ids[0] + "/items/" + driveFile["id"]
                    education_service.add_Submission_Resource(post["classId"],post["assignmentId"],driveFile["name"],resourceUrl,post["submissionId"])
    
        referer = request.META.get('HTTP_REFERER') 
        if referer.find("?")==-1:
            referer +="?tab=assignments"
        return HttpResponseRedirect(referer)

def uploadFileToOneDrive(resourceFolderURL,file,education_service):    
    ids = getIds(resourceFolderURL)
    return education_service.uploadFileToOneDrive(ids,file)


def getIds(resourceFolderURL):
    array = resourceFolderURL.split("/")
    length = len(array)
    return [array[length-3],array[length-1]]

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset
 