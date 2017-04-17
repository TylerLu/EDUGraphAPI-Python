from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate

from decorator import ms_login_required

from account.controller import LocalUserManager, O365UserManager

LOCAL_USER = LocalUserManager()
O365_USER = O365UserManager()

@ms_login_required
def aboutme(request):
    # get user info from session
    user_info = request.session['ms_user']
    user_info['showcolor'] = True
    user_info['color'] = LOCAL_USER.get_color(user_info)
    # color list
    colors = []
    colors.append({'value':'#2F19FF', 'name':'Blue'})
    colors.append({'value':'#127605', 'name':'Green'})
    colors.append({'value':'#535353', 'name':'Grey'})
    aad = authenticate(access_token=request.session['aad_token'], refresh_token=request.session['aad_refresh'], expires=request.session['aad_expires'], token_resource='aad', resource='aad')
    my_sections = settings.AAD_REQUEST.get_section_by_member(aad.access_token)
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
    user_info = request.session['ms_user']
    color = request.POST.get('favoritecolor')
    LOCAL_USER.update_color(color, user_info)
    user_info['color'] = LOCAL_USER.get_color(user_info)
    parameter = {}
    parameter['user'] = user_info
    parameter['colors'] = request.session['colors']
    parameter['groups'] = request.session['groups']
    parameter['savemessage'] = "<span class='saveresult'>Favorite color has been updated!</span>"
    return render(request, 'manage/aboutme.html', parameter)
