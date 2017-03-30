"""
account controller for local user and o365 user
"""

class LocalUser(object):
    
    def __init__(self, email, password):
        self.email = email
        self.password = password

class O365User(object):

    def __init__(self):
        pass

    def _check_admin(self, givenName):
        if givenName == 'Admin':
            return True
        return False
    
    def _check_role(self, uid, admin_ids):
        if uid in admin_ids:
            return 'Admin'
        return ''

    def parse_user_info(self, client, admin_ids=None):
        '''
        Gets sign in user info from MS Graph client
        '''
        user_obj = client.me.get()
        user_dict = user_obj.to_dict()
        user_info = {}
        user_info['islocal'] = False
        user_info['localexisted'] = False
        user_info['arelinked'] = False
        user_info['isauthenticated'] = True
        user_info['isadmin'] = self._check_admin(user_dict['givenName'])
        user_info['display_name'] = user_dict['displayName']
        if admin_ids:
            user_info['role'] = self._check_role(user_dict['id'], admin_ids)
        return user_info
    

        
