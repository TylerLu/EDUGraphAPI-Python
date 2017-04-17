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
    url(r'^Account/Login', account_views.my_login, name='login'),
    url(r'^Account/ReLogin', account_views.relogin, name='relogin'),
    url(r'^Account/O365login', account_views.o365_signin, name='o365signin'),
    url(r'^Account/ExternalLogin', account_views.external_login, name='exlogin'),
    url(r'^Account/Register', account_views.register, name='register'),

    url(r'^MS/Login', account_views.ms_login, name='ms_login'),
    

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
    url(r'^link/createlocal', link_views.createlocal, name='createlocal'),
    url(r'^link/loginlocal', link_views.loginlocal, name='loginlocal'),
    
    url(r'^Admin$', admin_views.admin, name='admin'),
    url(r'^Admin/LinkedAccounts', admin_views.linkaccounts, name='linkaccounts'),
    url(r'^UnlinkAccounts/(?P<link_id>\d+)', admin_views.unlinkaccounts, name='unlinkaccounts'),
    url(r'^Consent', admin_views.consent, name='consent'),
    url(r'^Unconsent', admin_views.unconsent, name='unconsent'),
]
