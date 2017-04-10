"""EDUGraphAPI URL Configuration

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
from django.conf.urls import include, url

from web import views as web_views

urlpatterns = [
    url(r'^$', web_views.index, name='index'),
    url(r'^Account/Login', web_views.login, name='login'),
    url(r'^Account/ReLogin', web_views.relogin, name='relogin'),
    url(r'^Account/O365login', web_views.o365_signin, name='o365signin'),
    url(r'^Account/ExternalLogin', web_views.external_login, name='exlogin'),
    url(r'^Account/Register', web_views.register, name='register'),

    url(r'^MS/Login', web_views.o365_login, name='o365login'),

    url(r'^Photo/UserPhoto/(?P<user_object_id>\w+-\w+-\w+-\w+-\w+)', web_views.photo, name='photo'),

    url(r'^Schools$', web_views.schools, name='schools'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Classes$', web_views.classes, name='classes'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Classes/Next', web_views.classnext, name='classnext'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Users$', web_views.users, name='users'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Users/Next', web_views.usernext, name='usernext'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Students/Next', web_views.studentnext, name='studentnext'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Teachers/Next', web_views.teachernext, name='teachernext'),
    url(r'^Schools/(?P<school_object_id>\w+-\w+-\w+-\w+-\w+)/Classes/(?P<class_object_id>\w+-\w+-\w+-\w+-\w+)', web_views.classdetails, name='classdetails'),
    url(r'^Schools/SaveSeatingArrangements$', web_views.saveseat, name='saveseat'),

    url(r'^Manage/AboutMe', web_views.aboutme, name='aboutme'),
    url(r'^Manage/UpdateFavoriteColor', web_views.updatecolor, name='updatecolor'),

    url(r'^link$', web_views.link, name='link'),
    url(r'^link/createlocal', web_views.createlocal, name='createlocal'),
    url(r'^link/loginlocal', web_views.loginlocal, name='loginlocal'),
    
    url(r'^Admin$', web_views.admin, name='admin'),
    url(r'^Admin/LinkedAccounts', web_views.linkaccounts, name='linkaccounts'),
    url(r'^UnlinkAccounts/(?P<link_id>\d+)', web_views.unlinkaccounts, name='unlinkaccounts'),
    url(r'^Consent', web_views.consent, name='consent'),
    url(r'^Unconsent', web_views.unconsent, name='unconsent'),
]
