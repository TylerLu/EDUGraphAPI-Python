"""
constant setting
"""

client_id = 'dfc81b95-1a9c-4522-9f33-259de9acf68b'

client_secret = 'yBjqwJkHMNOmh1LdgvO+xQsJ2KjlCTxjOeeidWV0rHM='

redirect_uri = 'http://127.0.0.1:8000/MS/Login'

login_base_uri = 'https://login.microsoftonline.com/common/oauth2/authorize?'

o365_signin_url = login_base_uri + 'response_type=code&client_id=%s&redirect_uri=%s' % (client_id, redirect_uri)

admin_consent_url = login_base_uri + 'response_type=code&client_id=%s&redirect_uri=%s&prompt=admin_consent' % (client_id, redirect_uri)

authorize_token_uri = 'https://login.microsoftonline.com/canvizEDU.onmicrosoft.com'

aad_resource = 'https://graph.windows.net'

ms_resource = 'https://graph.microsoft.com'

graph_base_uri = 'https://graph.microsoft.com/v1.0/'

company_admin_role_name = "Company Administrator";
