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
    url(r'^Account/ReLogin', account_views.relogin, name='relogin'),
    url(r'^Account/O365Login', account_views.o365_login, name='o365_login'),
    url(r'^Account/O365Signin', account_views.o365_signin, name='o365_signin'),
    url(r'^Account/Register', account_views.register, name='register'),
    url(r'^Account/LogOff', account_views.logoff, name='logoff'),

    url(r'^Auth/O365/Callback', account_views.o365_auth_callback, name='o365_auth_callback'),


    url(r'^Photo/UserPhoto/(?P<user_object_id>\w+-\w+-\w+-\w+-\w+)', account_views.photo, name='photo'),

    url(r'^Schools$', schools_views.schools, name='schools'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Classes$', schools_views.classes, name='classes'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Classes/Next', schools_views.classnext, name='classnext'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Users$', schools_views.users, name='users'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Users/Next', schools_views.usernext, name='usernext'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Students/Next', schools_views.studentnext, name='studentnext'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Teachers/Next', schools_views.teachernext, name='teachernext'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Classes/(?P<class_object_id>\w+-\w+-\w+-\w+-\w+)', schools_views.classdetails, name='classdetails'),
    url(r'^Schools/SaveSeatingArrangements$', schools_views.saveseat, name='saveseat'),

    url(r'^Manage/AboutMe', manage_views.aboutme, name='aboutme'),
    url(r'^Manage/UpdateFavoriteColor', manage_views.updatecolor, name='updatecolor'),

    url(r'^link$', link_views.link, name='link'),
    url(r'^link/createlocal', link_views.create_local, name='create_local'),
    url(r'^link/loginlocal', link_views.login_local, name='login_local'),
    url(r'^link/LoginO365', link_views.login_o365, name='login_o365'),
    url(r'^link/ProcessCode', link_views.process_code, name='link_process_code'),

    url(r'^Admin$', admin_views.admin, name='admin'),
    url(r'^Admin/LinkedAccounts', admin_views.linked_accounts, name='linked_accounts'),
    url(r'^UnlinkAccount/(?P<link_id>\d+)', admin_views.unlink_account, name='unlink_account'),
    url(r'^Admin/AddAppRoleAssignments', admin_views.add_app_roles, name='add_app_roles'),
    url(r'^Consent', admin_views.consent, name='consent'),
    url(r'^Unconsent', admin_views.unconsent, name='unconsent'),
    url(r'^Admin/Consent', admin_views.consent_alone, name='consent_alone'),
    url(r'^OnlyConsent', admin_views.only_consent, name='only_consent'),
]
