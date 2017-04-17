from django.conf import settings
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

import constant
from decorator import ms_login_required
from account.controller import LocalUserManager, O365UserManager
from .controller import SchoolProcesser

LOCAL_USER = LocalUserManager()
O365_USER = O365UserManager()

@ms_login_required
def schools(request):
    user_info = request.session['ms_user']
    print(user_info)
    # get token for aad api
    aad = authenticate(access_token=request.session['aad_token'], refresh_token=request.session['aad_refresh'], expires=request.session['aad_expires'], token_resource='aad', resource='aad')
    if not aad.access_token:
        if request.session.get(constant.username_cookie) and request.session.get(constant.email_cookie):
            return HttpResponseRedirect('/Account/O365login')
        else:
            return HttpResponseRedirect('/')
    # get schools info from aad graph api
    all_schools = settings.AAD_REQUEST.get_all_schools(aad.access_token)
    # process schools info for display
    school_processer = SchoolProcesser()
    out_schools = school_processer.normalize_schools_info(all_schools, user_info['school_id'])
    # set parameter for template
    parameter = {}
    parameter['user'] = user_info
    parameter['schools'] = out_schools
    return render(request, 'schools/index.html', parameter)

def classes(request, school_object_id):
    # get user info from session
    user_info = request.session['ms_user']
    user_info['isinaschool'] = True
    user_info['school_object_id'] = school_object_id
    aad = authenticate(access_token=request.session['aad_token'], refresh_token=request.session['aad_refresh'], expires=request.session['aad_expires'], token_resource='aad', resource='aad')

    school_processer = SchoolProcesser()
    # get a school info from aad graph api
    one_school = settings.AAD_REQUEST.get_one_school(aad.access_token, school_object_id)
    school_info = school_processer.normalize_one_school_info(one_school)
    # get sections info from aad graph api
    my_sections = settings.AAD_REQUEST.get_section_by_member(aad.access_token)
    all_sections, sectionsnextlink = settings.AAD_REQUEST.get_sections_by_schoolid(aad.access_token, school_info['school_id'])
    # process sections info for display
    my_out_sections, my_emails = school_processer.normalize_mysections_info(my_sections)
    out_sections = school_processer.normalize_sections_info(all_sections, my_emails)
    # get teachers from aad graph api for every section
    for section  in my_out_sections:
        all_teachers = settings.AAD_REQUEST.get_teachers_for_section(aad.access_token, section['object_id'])
        out_teachers = school_processer.normalize_teachers_info(all_teachers)
        section['teachers'] = out_teachers
    # set parameter for template
    parameter = {}
    parameter['user'] = user_info
    parameter['school'] = school_info
    parameter['sectionsnextlink'] = sectionsnextlink
    parameter['sections'] = out_sections
    parameter['mysections'] = my_out_sections
    return render(request, 'schools/classes.html', parameter)

def classnext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    aad = authenticate(access_token=request.session['aad_token'], refresh_token=request.session['aad_refresh'], expires=request.session['aad_expires'], token_resource='aad', resource='aad')

    school_processer = SchoolProcesser()
    # get a school info from aad graph api
    one_school = settings.AAD_REQUEST.get_one_school(aad.access_token, school_object_id)
    school_info = school_processer.normalize_one_school_info(one_school)
    # get sections info from aad graph api
    my_sections = settings.AAD_REQUEST.get_section_by_member(aad.access_token)
    next_sections, sectionsnextlink = settings.AAD_REQUEST.get_sections_by_schoolid(aad_token, school_info['school_id'], nextlink=nextlink)
    mysections, nextsections = school_processer.prune_next_sections(my_sections, next_sections)
    ajax_result = {}
    ajax_result['Sections'] = {}
    ajax_result['Sections']['Value'] = nextsections
    ajax_result['Sections']['NextLink'] = sectionsnextlink
    ajax_result['MySections'] = mysections
    return JsonResponse(ajax_result, safe=False)

def classdetails(request, school_object_id, class_object_id):
    # get user info from session
    user_info = request.session['ms_user']
    user_info['isinaschool'] = True
    user_info['school_object_id'] = school_object_id
    user_info['class_object_id'] = class_object_id
    user_info['color'] = LOCAL_USER.get_color(user_info)
    aad = authenticate(access_token=request.session['aad_token'], refresh_token=request.session['aad_refresh'], expires=request.session['aad_expires'], token_resource='aad', resource='aad')

    school_processer = SchoolProcesser()
    # get a school info from aad graph api
    one_school = settings.AAD_REQUEST.get_one_school(aad.access_token, school_object_id)
    school_info = school_processer.normalize_one_school_info(one_school)
    # get one section info from aad grap api
    one_section = settings.AAD_REQUEST.get_one_section(aad.access_token, class_object_id)
    section_info = school_processer.normalize_one_section_info(one_section)
    # get teachers from aad graph api
    all_teachers = settings.AAD_REQUEST.get_teachers_for_section(aad.access_token, class_object_id)
    out_teachers = school_processer.normalize_teachers_info(all_teachers)
    # get students from aad graph api
    all_students = settings.AAD_REQUEST.get_students_for_section(aad.access_token, class_object_id)
    out_students = school_processer.normalize_students_info(all_students)
    # get students position from database
    LOCAL_USER.get_positions(out_students, class_object_id)
    # get students colors from database
    LOCAL_USER.get_colors(out_students)
    # set seatrange
    seatrange = range(36)
    ms = authenticate(access_token=request.session['ms_token'], refresh_token=request.session['ms_refresh'], expires=request.session['ms_expires'], token_resource='ms', resource='ms')
    # get documents from ms graph api
    all_documents = settings.MS_REQUEST.get_documents_for_section(ms.access_token, class_object_id)
    documents_root = settings.MS_REQUEST.get_documents_root(ms.access_token, class_object_id)
    out_documents = school_processer.normalize_documents_info(all_documents)
    # get conversations from ms graph api
    all_conversations = settings.MS_REQUEST.get_conversatoins_for_section(ms.access_token, class_object_id)
    out_conversations = school_processer.normalize_conversations_info(all_conversations, section_info['email'])
    conversations_root = school_processer.get_conversations_root(section_info['email'])
    # set parameter for template
    parameter = {}
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

def saveseat(request):
    if request.is_ajax() and request.method == 'POST':
        seat_arrangements = json.loads(request.body.decode())
        LOCAL_USER.update_positions(seat_arrangements)
    return HttpResponse('save seat')

def users(request, school_object_id):
    # get user info from session
    user_info = request.session['ms_user']
    user_info['isinaschool'] = True
    user_info['school_object_id'] = school_object_id
    aad = authenticate(access_token=request.session['aad_token'], refresh_token=request.session['aad_refresh'], expires=request.session['aad_expires'], token_resource='aad', resource='aad')
    
    school_processer = SchoolProcesser()
    # get a school info from aad graph api
    one_school = settings.AAD_REQUEST.get_one_school(aad.access_token, school_object_id)
    school_info = school_processer.normalize_one_school_info(one_school)
    # get all users for school from aad graph api
    all_users, usersnextlink = settings.AAD_REQUEST.get_users_for_school(aad.access_token, school_object_id)
    out_users = school_processer.normalize_users_info(all_users)
    # get all teachers for school from aad graph api
    all_teachers, teachersnextlink = settings.AAD_REQUEST.get_teachers_by_schoolid(aad.access_token, user_info['school_id'])
    out_teachers = school_processer.normalize_teachers_info(all_teachers)
    # get students for school from aad graph api
    all_students, studentsnextlink = settings.AAD_REQUEST.get_students_by_schoolid(aad.access_token, user_info['school_id'])
    out_students = school_processer.normalize_students_info(all_students)
    # set parameter for template
    parameter = {}
    parameter['user'] = user_info
    parameter['school'] = school_info
    parameter['users'] = out_users
    parameter['teachers'] = out_teachers
    parameter['students'] = out_students
    parameter['usersnextlink'] = usersnextlink
    parameter['studentsnextlink'] = studentsnextlink
    parameter['teachersnextlink'] = teachersnextlink
    return render(request, 'schools/users.html', parameter)

def usernext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    user_info = request.session['ms_user']
    aad = authenticate(access_token=request.session['aad_token'], refresh_token=request.session['aad_refresh'], expires=request.session['aad_expires'], token_resource='aad', resource='aad')

    school_processer = SchoolProcesser()
    # get all users for school from aad graph api
    all_users, usersnextlink = settings.AAD_REQUEST.get_users_for_school(aad.access_token, school_object_id, nextlink=nextlink)
    out_users = school_processer.prune_users_info(all_users)
    ajax_result = {}
    ajax_result['Users'] = {}
    ajax_result['Users']['Value'] = out_users
    ajax_result['Users']['NextLink'] = usersnextlink
    return JsonResponse(ajax_result, safe=False)

def studentnext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    user_info = request.session['ms_user']
    aad = authenticate(access_token=request.session['aad_token'], refresh_token=request.session['aad_refresh'], expires=request.session['aad_expires'], token_resource='aad', resource='aad')
    
    school_processer = SchoolProcesser()
    # get all users for school from aad graph api
    all_students, studentsnextlink = settings.AAD_REQUEST.get_students_by_schoolid(aad.access_token, user_info['school_id'], nextlink=nextlink)
    out_students = school_processer.prune_students_info(all_students)
    ajax_result = {}
    ajax_result['Students'] = {}
    ajax_result['Students']['Value'] = out_students
    ajax_result['Students']['NextLink'] = studentsnextlink
    return JsonResponse(ajax_result, safe=False)

def teachernext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    user_info = request.session['ms_user']
    aad = authenticate(access_token=request.session['aad_token'], refresh_token=request.session['aad_refresh'], expires=request.session['aad_expires'], token_resource='aad', resource='aad')

    school_processer = SchoolProcesser()
    # get all users for school from aad graph api
    all_teachers, teachersnextlink = settings.AAD_REQUEST.get_teachers_by_schoolid(aad.access_token, user_info['school_id'], nextlink=nextlink)
    out_teachers = school_processer.prune_students_info(all_teachers)
    ajax_result = {}
    ajax_result['Teachers'] = {}
    ajax_result['Teachers']['Value'] = out_teachers
    ajax_result['Teachers']['NextLink'] = teachersnextlink
    return JsonResponse(ajax_result, safe=False)
