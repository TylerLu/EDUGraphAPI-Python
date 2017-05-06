'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import json
import constant
from utils.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from decorator import login_required
from services.token_service import TokenService
from services.auth_service import AuthService
from services.ms_graph_service import MSGraphService
from services.education_service import EducationService
from services.user_service import UserService

user_service = UserService()
token_service = TokenService()

@login_required
def schools(request):
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.AADGraph, user.o365_user_id)

    education_service = EducationService(user.tenant_id, token)
    my_school_id = education_service.get_my_school_id()
    school_user_id = education_service.get_school_user_id()
    schools = education_service.get_schools()
    # sort schools: my school will be put to the top
    schools.sort(key=lambda d:d['name'] if d['id'] == my_school_id else 'Z_' + d['name'])
    context = {
        'user': user,
        'my_school_id': my_school_id,
        'schools': schools,
        'school_user_id': school_user_id
    }
    return render(request, 'schools/index.html', context)

@login_required
def classes(request, school_object_id):
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.AADGraph, user.o365_user_id)

    education_service = EducationService(user.tenant_id, token)
    school = education_service.get_school(school_object_id)
    my_sections, mysection_emails = education_service.get_my_sections(school['id'])
    all_sections, sectionsnextlink = education_service.get_all_sections(school['id'], mysection_emails)

    context = {
        'user': user,
        'school': school,
        'sectionsnextlink': sectionsnextlink,
        'sections': all_sections,
        'mysections': my_sections,
        'school_object_id': school_object_id
    }
    return render(request, 'schools/classes.html', context)

@login_required
def classnext(request, school_object_id):    
    nextlink = request.GET.get('nextLink')
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.AADGraph, user.o365_user_id)

    education_service = EducationService(user.tenant_id, token)
    school = education_service.get_school(school_object_id)
    my_sections, mysection_emails = education_service.get_my_sections(school['id'])
    all_sections, sectionsnextlink = education_service.get_all_sections(school['id'], mysection_emails, nextlink=nextlink)

    ajax_result = {}
    ajax_result['Sections'] = {}
    ajax_result['Sections']['Value'] = all_sections
    ajax_result['Sections']['NextLink'] = sectionsnextlink
    ajax_result['MySections'] = my_sections
    return JsonResponse(ajax_result, safe=False)

@login_required
def classdetails(request, school_object_id, class_object_id):
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.AADGraph, user.o365_user_id)
    education_service = EducationService(user.tenant_id, token)

    school_info = education_service.get_school(school_object_id)
    section_info = education_service.get_section(class_object_id)
    teachers = education_service.get_section_members(class_object_id, 'Teacher')
    students = education_service.get_section_members(class_object_id, 'Student')

    # get students position from database
    user_service.get_positions(students, class_object_id)
    # get students colors from database
    for student in students:
        favorite_color = user_service.get_favorite_color_by_o365_user_id(student['uid'])
        if favorite_color:
            student['color'] = favorite_color
            
    # set seatrange
    seatrange = range(1, 37)

    ms_token = token_service.get_access_token(constant.Resources.MSGraph, user.o365_user_id)
    ms_graph_service = MSGraphService(ms_token)

    documents = ms_graph_service.get_documents(class_object_id)
    documents_root = ms_graph_service.get_documents_root(class_object_id)
    conversations = ms_graph_service.get_conversations(class_object_id, section_info['email'])
    conversations_root = ms_graph_service.get_conversations_root(section_info['email'])

    context = {
        'user': user,
        'school': school_info,
        'section': section_info,
        'teachers': teachers,
        'students': students,
        'documents': documents,
        'documents_root': documents_root,
        'conversations': conversations,
        'conversations_root': conversations_root,
        'seatrange': seatrange,
        'school_object_id': school_object_id,
        'class_object_id': class_object_id,
        'favoriate_color': '' #TODO
    }
    return render(request, 'schools/classdetails.html', context)

@login_required
def saveseat(request):
    if request.is_ajax() and request.method == 'POST':
        seat_arrangements = json.loads(request.body.decode())
        user_service.update_positions(seat_arrangements)
    return HttpResponse(json.dumps({'save':'ok'}))

@login_required
def users(request, school_object_id):
    user = AuthService.get_current_user(request)

    token = token_service.get_access_token(constant.Resources.AADGraph, user.o365_user_id)
    education_service = EducationService(user.tenant_id, token)

    school = education_service.get_school(school_object_id)
    users, usersnextlink = education_service.get_members(school_object_id)
    teachers, teachersnextlink = education_service.get_teachers(school['id'])
    students, studentsnextlink = education_service.get_students(school['id'])

    context = {
        'user': user,
        'school': school,
        'users': users,
        'teachers': teachers,
        'students': students,
        'usersnextlink': usersnextlink,
        'studentsnextlink': studentsnextlink,
        'teachersnextlink': teachersnextlink,
        'school_object_id': school_object_id
    }
    return render(request, 'schools/users.html', context)

@login_required
def usernext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.AADGraph, user.o365_user_id)
    education_service = EducationService(user.tenant_id, token)
    users, usersnextlink = education_service.get_members(school_object_id, nextlink=nextlink)

    ajax_result = {}
    ajax_result['Users'] = {}
    ajax_result['Users']['Value'] = users
    ajax_result['Users']['NextLink'] = usersnextlink
    return JsonResponse(ajax_result, safe=False)

@login_required
def studentnext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.AADGraph, user.o365_user_id)
    education_service = EducationService(user.tenant_id, token)    
    school = education_service.get_school(school_object_id)
    students, studentsnextlink = education_service.get_students(school['id'], nextlink=nextlink)

    ajax_result = {}
    ajax_result['Students'] = {}
    ajax_result['Students']['Value'] = students
    ajax_result['Students']['NextLink'] = studentsnextlink
    return JsonResponse(ajax_result, safe=False)

@login_required
def teachernext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    user = AuthService.get_current_user(request)
    token = token_service.get_access_token(constant.Resources.AADGraph, user.o365_user_id)
    education_service = EducationService(user.tenant_id, token)   
    school = education_service.get_school(school_object_id)
    teachers, teachersnextlink = education_service.get_students(school['id'], nextlink=nextlink)

    ajax_result = {}
    ajax_result['Teachers'] = {}
    ajax_result['Teachers']['Value'] = teachers
    ajax_result['Teachers']['NextLink'] = teachersnextlink
    return JsonResponse(ajax_result, safe=False)
