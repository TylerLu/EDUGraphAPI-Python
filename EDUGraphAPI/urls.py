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
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^Account/Login', web_views.login, name='login'),
    url(r'^Account/Register', web_views.register, name='register'),
    url(r'^Schools', web_views.schools, name='schools'),
    url(r'^Classes', web_views.classes, name='classes'),
    url(r'^Users', web_views.users, name='users'),
    url(r'^ClassDetails', web_views.classdetails, name='classdetails'),
    url(r'^AboutMe', web_views.aboutme, name='aboutme'),
    url(r'^link', web_views.link, name='link'),
]
