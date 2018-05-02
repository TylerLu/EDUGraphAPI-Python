'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import os

client_id = os.environ['ClientId']

client_secret = os.environ['ClientSecret']

source_code_repository_url = os.environ["SourceCodeRepositoryUrl"]


authority = 'https://login.microsoftonline.com/common/'

login_base_uri = 'https://login.microsoftonline.com/common/oauth2/authorize?'

log_out_url = 'https://login.microsoftonline.com/common/oauth2/logout?redirect_uri=%s&post_logout_redirect_uri=%s'

microsoft_certs_uri = 'https://login.microsoftonline.com/common/discovery/v2.0/keys'

company_admin_role_name = "Company Administrator"


mysql_host = os.environ['MySQLHost']

mysql_port = '3306'

mysql_name = 'edu'

mysql_user = os.environ['MySQLUser']

mysql_password = os.environ['MySQLPassword']


o365_username_cookie = "O365CookieUsername"

o365_email_cookie = "O365CookieEmail"

o365_user_session_key = '_o365_user'


favorite_colors = [
    {'value':'#2F19FF', 'name':'Blue'}, 
    {'value':'#127605', 'name':'Green'}, 
    {'value':'#535353', 'name':'Grey'}
]


class Resources():
    AADGraph = "https://graph.windows.net"
    MSGraph = "https://graph.microsoft.com"
    MSGraph_VERSION  ='beta'

class Roles():
    Admin = "Admin"
    Faculty = "Teacher"
    Student = "Student"