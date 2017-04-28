'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings

import json

import constant
from decorator import ms_login_required
from services.token_service import TokenService
from services.local_user_service import LocalUserService
from services.ms_graph_service import MSGraphService
from services.education_service import EducationService

LOCAL_USER = LocalUserService()
TOKEN_SERVICE = TokenService()
MSGRAPH_SERVICE = MSGraphService()
EDUCATION_SERVICE = EducationService()

@ms_login_required
def schools(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.session['ms_user']

    token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user_info['uid'])
    if not token:
        if request.session.get(constant.username_cookie) and request.session.get(constant.email_cookie):
            return HttpResponseRedirect('/Account/O365login')
        else:
            return HttpResponseRedirect('/')
    out_schools = EDUCATION_SERVICE.get_schools(token, user_info['school_id'])
    # set parameter for template
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['schools'] = out_schools
    return render(request, 'schools/index.html', parameter)

@ms_login_required
def classes(request, school_object_id):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    # get user info from session
    user_info = request.session['ms_user']
    user_info['isinaschool'] = True
    user_info['school_object_id'] = school_object_id

    token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user_info['uid'])
    school_info = EDUCATION_SERVICE.get_school(token, school_object_id)
    
    my_sections, mysection_emails = EDUCATION_SERVICE.get_my_sections(token, school_info['id'])
    all_sections, sectionsnextlink = EDUCATION_SERVICE.get_all_sections(token, school_info['id'], mysection_emails)

    # set parameter for template
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['school'] = school_info
    parameter['sectionsnextlink'] = sectionsnextlink
    parameter['sections'] = all_sections
    parameter['mysections'] = my_sections
    return render(request, 'schools/classes.html', parameter)

@ms_login_required
def classnext(request, school_object_id):
    nextlink = request.GET.get('nextLink')

    token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user_info['uid'])
    school_info = EDUCATION_SERVICE.get_school(token, school_object_id)

    my_sections, mysection_emails = EDUCATION_SERVICE.get_my_sections(token, school_info['id'])
    all_sections, sectionsnextlink = EDUCATION_SERVICE.get_all_sections(token, school_info['id'], mysection_emails, nextlink=nextlink)

    ajax_result = {}
    ajax_result['Sections'] = {}
    ajax_result['Sections']['Value'] = all_sections
    ajax_result['Sections']['NextLink'] = sectionsnextlink
    ajax_result['MySections'] = my_sections
    return JsonResponse(ajax_result, safe=False)

@ms_login_required
def classdetails(request, school_object_id, class_object_id):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    # get user info from session
    user_info = request.session['ms_user']
    user_info['isinaschool'] = True
    user_info['school_object_id'] = school_object_id
    user_info['class_object_id'] = class_object_id
    user_info['color'] = LOCAL_USER.get_color(user_info)

    token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user_info['uid'])
    school_info = EDUCATION_SERVICE.get_school(token, school_object_id)
    section_info = EDUCATION_SERVICE.get_section(token, class_object_id)

    out_teachers = EDUCATION_SERVICE.get_section_members(token, class_object_id, 'Teacher')
    out_students = EDUCATION_SERVICE.get_section_members(token, class_object_id, 'Student')

    # get students position from database
    LOCAL_USER.get_positions(out_students, class_object_id)
    # get students colors from database
    LOCAL_USER.get_colors(out_students)
    # set seatrange
    seatrange = range(1, 37)

    ms_token = TOKEN_SERVICE.get_access_token(constant.Resources.MSGraph, user_info['uid'])
    out_documents = MSGRAPH_SERVICE.get_documents(ms_token, class_object_id)
    documents_root = MSGRAPH_SERVICE.get_documents_root(ms_token, class_object_id)

    out_conversations = MSGRAPH_SERVICE.get_conversations(ms_token, class_object_id, section_info['email'])
    conversations_root = MSGRAPH_SERVICE.get_conversations_root(section_info['email'])

    # set parameter for template
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['school'] = school_info
    parameter['section'] = section_info
    parameter['teachers'] = out_teachers
    parameter['students'] = out_students
    parameter['documents'] = out_documents
    parameter['documents_root'] = documents_root
    parameter['conversations'] = out_conversations
    parameter['conversations_root'] = conversations_root
    parameter['seatrange'] = seatrange
    return render(request, 'schools/classdetails.html', parameter)

@ms_login_required
def saveseat(request):
    if request.is_ajax() and request.method == 'POST':
        seat_arrangements = json.loads(request.body.decode())
        LOCAL_USER.update_positions(seat_arrangements)
    return HttpResponse(json.dumps({'save':'ok'}))

@ms_login_required
def users(request, school_object_id):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    # get user info from session
    user_info = request.session['ms_user']
    user_info['isinaschool'] = True
    user_info['school_object_id'] = school_object_id
    
    token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user_info['uid'])
    school_info = EDUCATION_SERVICE.get_school(token, school_object_id)
    
    out_users, usersnextlink = EDUCATION_SERVICE.get_members(token, school_object_id)

    out_teachers, teachersnextlink = EDUCATION_SERVICE.get_teachers(token, school_info['id'])

    out_students, studentsnextlink = EDUCATION_SERVICE.get_students(token, school_info['id'])

    # set parameter for template
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['school'] = school_info
    parameter['users'] = out_users
    parameter['teachers'] = out_teachers
    parameter['students'] = out_students
    parameter['usersnextlink'] = usersnextlink
    parameter['studentsnextlink'] = studentsnextlink
    parameter['teachersnextlink'] = teachersnextlink
    return render(request, 'schools/users.html', parameter)

@ms_login_required
def usernext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    user_info = request.session['ms_user']
    
    token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user_info['uid'])
    out_users, usersnextlink = EDUCATION_SERVICE.get_members(token, school_object_id, nextlink=nextlink)

    ajax_result = {}
    ajax_result['Users'] = {}
    ajax_result['Users']['Value'] = out_users
    ajax_result['Users']['NextLink'] = usersnextlink
    return JsonResponse(ajax_result, safe=False)

@ms_login_required
def studentnext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    user_info = request.session['ms_user']
    
    token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user_info['uid'])
    out_students, studentsnextlink = EDUCATION_SERVICE.get_students(token, user_info['school_id'], nextlink=nextlink)

    ajax_result = {}
    ajax_result['Students'] = {}
    ajax_result['Students']['Value'] = out_students
    ajax_result['Students']['NextLink'] = studentsnextlink
    return JsonResponse(ajax_result, safe=False)

@ms_login_required
def teachernext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    user_info = request.session['ms_user']

    token = TOKEN_SERVICE.get_access_token(constant.Resources.AADGraph, user_info['uid'])
    out_teachers, teachersnextlink = EDUCATION_SERVICE.get_students(token, user_info['school_id'], nextlink=nextlink)

    ajax_result = {}
    ajax_result['Teachers'] = {}
    ajax_result['Teachers']['Value'] = out_teachers
    ajax_result['Teachers']['NextLink'] = teachersnextlink
    return JsonResponse(ajax_result, safe=False)
