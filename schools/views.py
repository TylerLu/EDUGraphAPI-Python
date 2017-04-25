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
from services.user_service import LocalUserService
from services.education_service import SchoolService

LOCAL_USER = LocalUserService()
TOKEN_SERVICE = TokenService()
SCHOOL_SERVICE = SchoolService()

@ms_login_required
def schools(request):
    links = settings.DEMO_HELPER.get_links(request.get_full_path())
    user_info = request.session['ms_user']
    # get token for aad api
    access_token = TOKEN_SERVICE.get_access_token('aad')
    if not access_token:
        if request.session.get(constant.username_cookie) and request.session.get(constant.email_cookie):
            return HttpResponseRedirect('/Account/O365login')
        else:
            return HttpResponseRedirect('/')
    out_schools = SCHOOL_SERVICE.get_user_schools(user_info['school_id'])
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

    school_info = SCHOOL_SERVICE.get_class_school(school_object_id)

    my_out_classes, my_emails = SCHOOL_SERVICE.get_user_classes(school_info['id'])
    all_out_classes, classesnextlink = SCHOOL_SERVICE.get_school_classes(school_info['id'], my_emails)

    # get teachers from aad graph api for every section
    for section  in my_out_classes:
        out_teachers = SCHOOL_SERVICE.get_class_teachers(section['object_id'])
        section['teachers'] = out_teachers

    # set parameter for template
    parameter = {}
    parameter['links'] = links
    parameter['user'] = user_info
    parameter['school'] = school_info
    parameter['sectionsnextlink'] = classesnextlink
    parameter['sections'] = all_out_classes
    parameter['mysections'] = my_out_classes
    return render(request, 'schools/classes.html', parameter)

@ms_login_required
def classnext(request, school_object_id):
    nextlink = request.GET.get('nextLink')

    school_info = SCHOOL_SERVICE.get_class_school(school_object_id)

    my_out_classes, my_emails = SCHOOL_SERVICE.get_user_classes(school_info['id'])
    all_out_classes, classesnextlink = SCHOOL_SERVICE.get_school_classes(school_info['id'], my_emails)

    mysections, nextsections = SCHOOL_SERVICE.get_next_classes(school_info['id'], classesnextlink, my_out_classes)

    ajax_result = {}
    ajax_result['Sections'] = {}
    ajax_result['Sections']['Value'] = nextsections
    ajax_result['Sections']['NextLink'] = classesnextlink
    ajax_result['MySections'] = mysections
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

    school_info = SCHOOL_SERVICE.get_class_school(school_object_id)

    section_info = SCHOOL_SERVICE.get_current_class(class_object_id)

    out_teachers = SCHOOL_SERVICE.get_class_teachers(class_object_id)

    out_students = SCHOOL_SERVICE.get_class_students(class_object_id)

    # get students position from database
    LOCAL_USER.get_positions(out_students, class_object_id)
    # get students colors from database
    LOCAL_USER.get_colors(out_students)
    # set seatrange
    seatrange = range(1, 37)

    out_documents = SCHOOL_SERVICE.get_documents(class_object_id)
    documents_root = SCHOOL_SERVICE.get_documents_root(class_object_id)

    out_conversations = SCHOOL_SERVICE.get_conversations(class_object_id, section_info['email'])
    conversations_root = SCHOOL_SERVICE.get_conversations_root(section_info['email'])

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
    
    school_info = SCHOOL_SERVICE.get_class_school(school_object_id)
    
    out_users, usersnextlink = SCHOOL_SERVICE.get_current_users(school_object_id)

    out_teachers, teachersnextlink = SCHOOL_SERVICE.get_current_teachers(school_info['id'])

    out_students, studentsnextlink = SCHOOL_SERVICE.get_current_students(school_info['id'])
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

    out_users, usersnextlink = SCHOOL_SERVICE.get_next_users(school_object_id, nextlink)

    ajax_result = {}
    ajax_result['Users'] = {}
    ajax_result['Users']['Value'] = out_users
    ajax_result['Users']['NextLink'] = usersnextlink
    return JsonResponse(ajax_result, safe=False)

@ms_login_required
def studentnext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    user_info = request.session['ms_user']
    
    out_students, studentsnextlink = SCHOOL_SERVICE.get_next_students(user_info['school_id'], nextlink)

    ajax_result = {}
    ajax_result['Students'] = {}
    ajax_result['Students']['Value'] = out_students
    ajax_result['Students']['NextLink'] = studentsnextlink
    return JsonResponse(ajax_result, safe=False)

@ms_login_required
def teachernext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    user_info = request.session['ms_user']

    out_teachers, teachersnextlink = SCHOOL_SERVICE.get_next_teachers(user_info['school_id'], nextlink)

    ajax_result = {}
    ajax_result['Teachers'] = {}
    ajax_result['Teachers']['Value'] = out_teachers
    ajax_result['Teachers']['NextLink'] = teachersnextlink
    return JsonResponse(ajax_result, safe=False)
