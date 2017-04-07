import os
import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.conf import settings

from .utils import constant
from .utils.token_controller import TokenManager
from .utils.ms_api_request import MSGraphRequest
from .utils.aad_api_request import AADGraphRequest
from .utils.schools_controller import SchoolProcesser
from .utils.account_controller import LocalUser, O365User

from .forms import UserInfo, UserRegInfo

TOKEN_MANAGER = TokenManager()
AAD_REQUEST = TOKEN_MANAGER.aad_request()
MS_REQUEST = TOKEN_MANAGER.ms_request()
LOCAL_USER = LocalUser()
O365_USER = O365User()

def index(request):
    user_form = UserInfo()
    if request.session[constant.username_cookie] and request.session[constant.email_cookie]:
        return HttpResponseRedirect('/Schools')
    return render(request, 'account/login.html', {'user_form':user_form})

def relogin(request):
    user_form = UserInfo()
    return render(request, 'account/login.html', {'user_form':user_form})

def login(request):
    email = ''
    password = ''
    errors = []
    if request.method == 'POST':
        user_input_form = UserInfo(request.POST)
        if user_input_form.is_valid():
            data = user_input_form.clean()
            email = data['Email']
            password = data['Password']
        success = LOCAL_USER.check_login(data)
        if success == False:
            errors.append('Invalid login attempt.')
    if email and password:
        if errors:
            user_form = UserInfo()
            return render(request, 'account/login.html', {'user_form':user_form, 'errors':errors})
    return HttpResponseRedirect(constant.o365_signin_url)

def check_link(user_info):
    LOCAL_USER.check_status(user_info)

def o365_login(request):
    code = request.GET.get('code', '')
    # get aad resource token
    aad_token = TOKEN_MANAGER.get_token_by_code(code, 'aad')
    # get admin ids from aad graph api because of ms graph lost directoryRoles members api
    admin_ids = AAD_REQUEST.get_admin_ids(aad_token)
    # get assigned_licenses skuIDs from aad graph api because of ms graph lost assigned licenses api
    extra_info  = AAD_REQUEST.get_user_extra_info(aad_token)
    # get ms resource token
    ms_token = TOKEN_MANAGER.get_token('ms')
    ms_client = MS_REQUEST.get_client(ms_token)
    # process user info for display
    user_info = O365_USER.normalize_user_info(ms_client, extra_info, admin_ids)
    # check_link_status
    check_link(user_info)
    # restore user info to session for pages
    request.session['o365_user_info'] = user_info
    request.session[constant.username_cookie] = user_info['display_name']
    request.session[constant.email_cookie] = user_info['mail']
    if user_info['arelinked']:
        if user_info['role'] != 'Admin':
            return HttpResponseRedirect('/Schools')
        else:
            return HttpResponseRedirect('/Admin')
    else:
        return HttpResponseRedirect('/link')

def o365_signin(request):
    username = request.session[constant.username_cookie]
    email = request.session[constant.email_cookie]
    parameter = {}
    parameter['username'] = username
    parameter['email'] = email
    return render(request, 'account/O365login.html', parameter)

def external_login(request):
    return HttpResponseRedirect(constant.o365_signin_url)

def register(request):
    user_reg_form = UserRegInfo()
    email = ''
    password = ''
    favoritecolor = ''
    if request.method == 'POST':
        user_reg_form = UserRegInfo(request.POST)
        if user_reg_form.is_valid():
            data = user_reg_form.clean()
            ret = LOCAL_USER.register(data)
            if ret:
                return HttpResponseRedirect('/')
    return render(request, 'account/register.html', {'user_reg_form':user_reg_form})

def link(request):
    user_info = request.session['o365_user_info']
    # set parameter for template
    parameter = {}
    parameter['user'] = user_info
    return render(request, 'manage/link.html', parameter)

def createlocal(request):
    user_info = request.session['o365_user_info']
    LOCAL_USER.create(user_info)
    user_info['arelinked'] = True
    return HttpResponseRedirect('/Schools')

def loginlocal(request):
    user_info = request.session['o365_user_info']
    LOCAL_USER.link(user_info)
    user_info['arelinked'] = True
    return HttpResponseRedirect('/Schools')

def photo(request, user_object_id):
    # get token for ms api
    ms_token = TOKEN_MANAGER.get_token('ms')
    # get user photo from ms graph api
    user_photo = MS_REQUEST. get_user_photo(ms_token, user_object_id)
    if not user_photo:
        local_photo_path = settings.STATICFILES_DIRS[0] + '/Images/DefaultUserPhoto.jpg'
        local_photo_file = open(local_photo_path, 'rb')
        user_photo = local_photo_file.read()
    return HttpResponse(user_photo, content_type='image/jpeg')

def schools(request):
    # get user info from session
    user_info = request.session['o365_user_info']
    # get token for aad api
    aad_token = TOKEN_MANAGER.get_token('aad')
    if not aad_token:
        if request.session[constant.username_cookie] and request.session[constant.email_cookie]:
            return HttpResponseRedirect('/Account/O365login')
        else:
            return HttpResponseRedirect('/')
    # get schools info from aad graph api
    all_schools = AAD_REQUEST.get_all_schools(aad_token)
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
    user_info = request.session['o365_user_info']
    user_info['isinaschool'] = True
    user_info['school_object_id'] = school_object_id
    # get token for aad api
    aad_token = TOKEN_MANAGER.get_token('aad')

    school_processer = SchoolProcesser()
    # get a school info from aad graph api
    one_school = AAD_REQUEST.get_one_school(aad_token, school_object_id)
    school_info = school_processer.normalize_one_school_info(one_school)
    # get sections info from aad graph api
    my_sections = AAD_REQUEST.get_section_by_member(aad_token)
    all_sections, sectionsnextlink = AAD_REQUEST.get_sections_by_schoolid(aad_token, school_info['school_id'])
    # process sections info for display
    my_out_sections, my_emails = school_processer.normalize_mysections_info(my_sections)
    out_sections = school_processer.normalize_sections_info(all_sections, my_emails)
    # get teachers from aad graph api for every section
    for section  in my_out_sections:
        all_teachers = AAD_REQUEST.get_teachers_for_section(aad_token, section['object_id'])
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
    # get token for aad api
    aad_token = TOKEN_MANAGER.get_token('aad')

    school_processer = SchoolProcesser()
    # get a school info from aad graph api
    one_school = AAD_REQUEST.get_one_school(aad_token, school_object_id)
    school_info = school_processer.normalize_one_school_info(one_school)
    # get sections info from aad graph api
    my_sections = AAD_REQUEST.get_section_by_member(aad_token)
    next_sections, sectionsnextlink = AAD_REQUEST.get_sections_by_schoolid(aad_token, school_info['school_id'], nextlink=nextlink)
    mysections, nextsections = school_processer.prune_next_sections(my_sections, next_sections)
    ajax_result = {}
    ajax_result['Sections'] = {}
    ajax_result['Sections']['Value'] = nextsections
    ajax_result['Sections']['NextLink'] = sectionsnextlink
    ajax_result['MySections'] = mysections
    return JsonResponse(ajax_result, safe=False)

def classdetails(request, school_object_id, class_object_id):
    # get user info from session
    user_info = request.session['o365_user_info']
    user_info['isinaschool'] = True
    user_info['school_object_id'] = school_object_id
    user_info['class_object_id'] = class_object_id
    user_info['color'] = LOCAL_USER.get_color(user_info)
    # get token for aad api
    aad_token = TOKEN_MANAGER.get_token('aad')

    school_processer = SchoolProcesser()
    # get a school info from aad graph api
    one_school = AAD_REQUEST.get_one_school(aad_token, school_object_id)
    school_info = school_processer.normalize_one_school_info(one_school)
    # get one section info from aad grap api
    one_section = AAD_REQUEST.get_one_section(aad_token, class_object_id)
    section_info = school_processer.normalize_one_section_info(one_section)
    # get teachers from aad graph api
    all_teachers = AAD_REQUEST.get_teachers_for_section(aad_token, class_object_id)
    out_teachers = school_processer.normalize_teachers_info(all_teachers)
    # get students from aad graph api
    all_students = AAD_REQUEST.get_students_for_section(aad_token, class_object_id)
    out_students = school_processer.normalize_students_info(all_students)
    # get students position from database
    LOCAL_USER.get_positions(out_students, class_object_id)
    # get students colors from database
    LOCAL_USER.get_colors(out_students)
    # set seatrange
    seatrange = range(36)
    # get token for ms api
    ms_token = TOKEN_MANAGER.get_token('ms')
    # get documents from ms graph api
    all_documents = MS_REQUEST.get_documents_for_section(ms_token, class_object_id)
    documents_root = MS_REQUEST.get_documents_root(ms_token, class_object_id)
    out_documents = school_processer.normalize_documents_info(all_documents)
    # get conversations from ms graph api
    all_conversations = MS_REQUEST.get_conversatoins_for_section(ms_token, class_object_id)
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
    user_info = request.session['o365_user_info']
    user_info['isinaschool'] = True
    user_info['school_object_id'] = school_object_id
    # get token for aad api
    aad_token = TOKEN_MANAGER.get_token('aad')
    
    school_processer = SchoolProcesser()
    # get a school info from aad graph api
    one_school = AAD_REQUEST.get_one_school(aad_token, school_object_id)
    school_info = school_processer.normalize_one_school_info(one_school)
    # get all users for school from aad graph api
    all_users, usersnextlink = AAD_REQUEST.get_users_for_school(aad_token, school_object_id)
    out_users = school_processer.normalize_users_info(all_users)
    # get all teachers for school from aad graph api
    all_teachers, teachersnextlink = AAD_REQUEST.get_teachers_by_schoolid(aad_token, user_info['school_id'])
    out_teachers = school_processer.normalize_teachers_info(all_teachers)
    # get students for school from aad graph api
    all_students, studentsnextlink = AAD_REQUEST.get_students_by_schoolid(aad_token, user_info['school_id'])
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
    # get user info from session
    user_info = request.session['o365_user_info']
    # get token for aad api
    aad_token = TOKEN_MANAGER.get_token('aad')

    school_processer = SchoolProcesser()
    # get all users for school from aad graph api
    all_users, usersnextlink = AAD_REQUEST.get_users_for_school(aad_token, school_object_id, nextlink=nextlink)
    out_users = school_processer.prune_users_info(all_users)
    ajax_result = {}
    ajax_result['Users'] = {}
    ajax_result['Users']['Value'] = out_users
    ajax_result['Users']['NextLink'] = usersnextlink
    return JsonResponse(ajax_result, safe=False)

def studentnext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    # get user info from session
    user_info = request.session['o365_user_info']
    # get token for aad api
    aad_token = TOKEN_MANAGER.get_token('aad')

    school_processer = SchoolProcesser()
    # get all users for school from aad graph api
    all_students, studentsnextlink = AAD_REQUEST.get_students_by_schoolid(aad_token, user_info['school_id'], nextlink=nextlink)
    out_students = school_processer.prune_students_info(all_students)
    ajax_result = {}
    ajax_result['Students'] = {}
    ajax_result['Students']['Value'] = out_students
    ajax_result['Students']['NextLink'] = studentsnextlink
    return JsonResponse(ajax_result, safe=False)

def teachernext(request, school_object_id):
    nextlink = request.GET.get('nextLink')
    # get user info from session
    user_info = request.session['o365_user_info']
    # get token for aad api
    aad_token = TOKEN_MANAGER.get_token('aad')

    school_processer = SchoolProcesser()
    # get all users for school from aad graph api
    all_teachers, teachersnextlink = AAD_REQUEST.get_teachers_by_schoolid(aad_token, user_info['school_id'], nextlink=nextlink)
    out_teachers = school_processer.prune_students_info(all_teachers)
    ajax_result = {}
    ajax_result['Teachers'] = {}
    ajax_result['Teachers']['Value'] = out_teachers
    ajax_result['Teachers']['NextLink'] = teachersnextlink
    return JsonResponse(ajax_result, safe=False)

def aboutme(request):
    # get user info from session
    user_info = request.session['o365_user_info']
    user_info['showcolor'] = True
    user_info['color'] = LOCAL_USER.get_color(user_info)
    # color list
    colors = []
    colors.append({'value':'#2F19FF', 'name':'Blue'})
    colors.append({'value':'#127605', 'name':'Green'})
    colors.append({'value':'#535353', 'name':'Grey'})
    # get token for aad api
    aad_token = TOKEN_MANAGER.get_token('aad')
    my_sections = AAD_REQUEST.get_section_by_member(aad_token)
    groups = []
    for section in my_sections:
        groups.append(section['displayName'])
    parameter = {}
    parameter['user'] = user_info
    parameter['colors'] = colors
    parameter['groups'] = groups
    request.session['colors'] = colors
    request.session['groups'] = groups
    return render(request, 'manage/aboutme.html', parameter)

def updatecolor(request):
    # get user info from session
    user_info = request.session['o365_user_info']
    color = request.POST.get('favoritecolor')
    LOCAL_USER.update_color(color, user_info)
    user_info['color'] = LOCAL_USER.get_color(user_info)
    parameter = {}
    parameter['user'] = user_info
    parameter['colors'] = request.session['colors']
    parameter['groups'] = request.session['groups']
    parameter['savemessage'] = "<span class='saveresult'>Favorite color has been updated!</span>"
    return render(request, 'manage/aboutme.html', parameter)

def admin(request):
    # get user info from session
    user_info = request.session['o365_user_info']
    user_info['isadminconsented'] = True
    parameter = {}
    parameter['user'] = user_info
    return render(request, 'admin/index.html', parameter)

def linkaccounts(request):
    # get user info from session
    user_info = request.session['o365_user_info']
    links = LOCAL_USER.get_links()
    parameter = {}
    parameter['user'] = user_info
    parameter['links'] = links
    return render(request, 'admin/linkedaccounts.html', parameter)

def unlinkaccounts(request, link_id):
    # get user info from session
    user_info = request.session['o365_user_info']
    LOCAL_USER.remove_link(link_id)
    links = LOCAL_USER.get_links()
    parameter = {}
    parameter['user'] = user_info
    parameter['links'] = links
    return render(request, 'admin/linkedaccounts.html', parameter)

def consent(request):
    return HttpResponseRedirect(constant.admin_consent_url)

def unconsent(request):
    # get user info from session
    user_info = request.session['o365_user_info']
    user_info['isadminconsented'] = False
    parameter = {}
    parameter['user'] = user_info
    return render(request, 'admin/index.html', parameter)
