'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from account import views as account_views
from schools import views as schools_views
from managements import views as manage_views
from link import views as link_views
from admin import views as admin_views

urlpatterns = [
    url(r'^$', account_views.index, name='index'),
    url(r'^Account/Login', account_views.login, name='login'),
    url(r'^Account/Reset', account_views.reset, name='reset'),
    url(r'^Account/O365Login', account_views.o365_login, name='o365_login'),
    url(r'^Account/Register', account_views.register, name='register'),
    url(r'^Account/LogOff', account_views.logoff, name='logoff'),

    url(r'^Auth/O365/Callback', account_views.o365_auth_callback, name='o365_auth_callback'),


    url(r'^Photo/UserPhoto/(?P<user_object_id>\w+-\w+-\w+-\w+-\w+)', account_views.photo, name='photo'),

    url(r'^Schools$', schools_views.schools, name='schools'),
    url(r'^Schools/(?P<school_id>\w+-\w+-\w+-\w+-\w+)/Classes$', schools_views.classes, name='classes'),
    url(r'^Schools/(?P<school_id>\w+-\w+-\w+-\w+-\w+)/Classes/Next', schools_views.classes_next, name='classes_next'),
    url(r'^Schools/(?P<school_id>\w+-\w+-\w+-\w+-\w+)/Classes/(?P<class_id>\w+-\w+-\w+-\w+-\w+)', schools_views.class_details, name='class_details'),
    url(r'^Class/(?P<class_id>\w+-\w+-\w+-\w+-\w+)/Coteacher/(?P<user_object_id>\w+-\w+-\w+-\w+-\w+)', schools_views.add_coteacher, name='add_coteacher'),
    url(r'^Schools/SaveSeatingArrangements$', schools_views.save_seating_arrangements, name='save_seating_arrangements'),
    url(r'^Schools/newAssignment$', schools_views.new_assignment, name='new_assignment'),
    url(r'^Class/(?P<class_id>\w+-\w+-\w+-\w+-\w+)/Assignment/(?P<assignment_id>\w+-\w+-\w+-\w+-\w+)/Resources', schools_views.get_assignment_resources, name='get_assignment_resources'),
    url(r'^Class/updateAssignment$', schools_views.update_assignment, name='update_assignment'),
    url(r'^Class/(?P<class_id>\w+-\w+-\w+-\w+-\w+)/Assignment/(?P<assignment_id>\w+-\w+-\w+-\w+-\w+)/getAssignmentResourcesSubmission', schools_views.get_assignment_submission_resources, name='get_assignment_submission_resources'),
    url(r'^Class/(?P<class_id>\w+-\w+-\w+-\w+-\w+)/Assignment/(?P<assignment_id>\w+-\w+-\w+-\w+-\w+)/getSubmissions', schools_views.get_submissions, name='get_submissions'),

    url(r'^Manage/AboutMe', manage_views.aboutme, name='aboutme'),
    url(r'^Manage/UpdateFavoriteColor', manage_views.updatecolor, name='updatecolor'),

    url(r'^Link$', link_views.link, name='link'),
    url(r'^Link/CreateLocal', link_views.create_local, name='create_local'),
    url(r'^Link/LoginLocal', link_views.login_local, name='login_local'),
    url(r'^Link/LoginO365', link_views.login_o365, name='login_o365'),
    url(r'^Link/ProcessCode', link_views.process_code, name='link_process_code'),

    url(r'^Admin$', admin_views.admin, name='admin'),
    url(r'^Admin/LinkedAccounts', admin_views.linked_accounts, name='linked_accounts'),
    url(r'^Admin/ProcessCode', admin_views.process_code, name='admin_process_code'),
    url(r'^UnlinkAccount/(?P<link_id>\d+)', admin_views.unlink_account, name='unlink_account'),
    url(r'^Admin/AddAppRoleAssignments', admin_views.add_app_role_assignments, name='add_app_role_assignments'),
    url(r'^Consent', admin_views.consent, name='consent'),
    url(r'^Unconsent', admin_views.unconsent, name='unconsent'),
    url(r'^Admin/Consent', admin_views.consent_alone, name='consent_alone'),
    url(r'^Admin/ClearLoginCache',admin_views.clear_login_cache,name='clear_login_cache'),
]