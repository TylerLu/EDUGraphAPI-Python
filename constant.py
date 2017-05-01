'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
import os

client_id = os.environ['ClientId']

client_secret = os.environ['ClientSecret']

redirect_uri = '%s://%s/Auth/O365/Callback'

login_base_uri = 'https://login.microsoftonline.com/common/oauth2/authorize?'

o365_signin_url = login_base_uri + 'response_type=code&client_id=%s&redirect_uri=%s' % (client_id, redirect_uri)

o365_login_url = login_base_uri + 'response_type=code&client_id=%s&prompt=login&redirect_uri=' % (client_id)

admin_consent_url = login_base_uri + 'response_type=code&client_id=%s&redirect_uri=%s&prompt=admin_consent' % (client_id, redirect_uri)

log_out_url = 'https://login.microsoftonline.com/common/oauth2/logout?redirect_uri=%s&post_logout_redirect_uri=%s'

authorize_token_uri = 'https://login.microsoftonline.com/canvizEDU.onmicrosoft.com'

company_admin_role_name = "Company Administrator"

bing_map_key = os.environ['BingMapKey']

username_cookie = "O365CookieUsername"

email_cookie = "O365CookieEmail"

class Resources():
    AADGraph = "https://graph.windows.net/"
    MSGraph = "https://graph.microsoft.com/"

class Roles():
    Admin = "Admin"
    Faculty = "Faculty"
    Student = "Student"

class O365ProductLicenses():
    #Microsoft Classroom Preview
    Classroom = "80f12768-d8d9-4e93-99a8-fa2464374d34"
    #Office 365 Education for faculty
    Faculty = "94763226-9b3c-4e75-a931-5c89701abe66"
    #Office 365 Education for students
    Student = "314c4481-f395-4525-be8b-2ec4bb1e9d91"
    #Office 365 Education for faculty
    FacultyPro = "78e66a63-337a-4a9a-8959-41c6654dfb56"
    #Office 365 Education for students
    StudentPro = "e82ae690-a2d5-4d76-8d30-7c6e01e6022e"


FavoriteColors = [{'value':'#2F19FF', 'name':'Blue'}, {'value':'#127605', 'name':'Green'}, {'value':'#535353', 'name':'Grey'}]
