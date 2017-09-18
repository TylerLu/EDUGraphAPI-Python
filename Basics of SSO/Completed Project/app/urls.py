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

urlpatterns = [
    url(r'^$', account_views.index, name='index'),
    url(r'^Account/Login', account_views.login, name='login'), 
    url(r'^Account/Register', account_views.register, name='register'),
    url(r'^Account/LogOff', account_views.logoff, name='logoff'),
    url(r'^Account/O365Login', account_views.o365_login, name='o365_login'),
    url(r'^Auth/O365/Callback', account_views.o365_auth_callback, name='o365_auth_callback'),
    url(r'^Schools$', schools_views.schools, name='schools'),
]