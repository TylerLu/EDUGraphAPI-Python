from constant import Roles
from constant import O365ProductLicenses

from services.ms_graph_service import MSGraphService
from services.aad_graph_service import AADGraphService

class O365UserService(object):

    def __init__(self):
        self._aad_api_service = AADGraphService()
        self._ms_api_service = MSGraphService()

    def _check_admin(self, role):
        if role == 'Admin':
            return True
        return False
    
    def _check_role(self, uid, admin_ids, sku_ids):
        roles = []
        role = ''
        if uid in admin_ids:
            roles.append('Admin')
        else:
            for sid in sku_ids:
                if sid == O365ProductLicenses.Faculty or sid == O365ProductLicenses.FacultyPro:
                    roles.append(Roles.Faculty)
                if sid == O365ProductLicenses.Student or sid == O365ProductLicenses.StudentPro:
                    roles.append(Roles.Student)
        if roles:
            if 'Admin' in roles:
                role = 'Admin'
            elif 'Faculty' in roles:
                role = 'Teacher'
            elif 'Student' in roles:
                role = 'Student'
        return role
    
    def _check_student(self, role):
        if role == 'Student':
            return True
        return False

    def _assign_full_name(self, user_dict):
        given_name = user_dict['givenName'].strip()
        sur_name = user_dict['surname'].strip()
        if given_name and sur_name:
            full_name = given_name + ' ' + sur_name
        else:
            full_name = user_dict['displayName']
        return full_name
    
    def _assign_photo(self, uid):
        photo = '/Photo/UserPhoto/%s' % uid
        return photo
    
    def _assign_mail(self, user_dict):
        mail = ''
        if not user_dict['mail']:
            mail = user_dict['userPrincipalName']
        else:
            mail = user_dict['mail']
        return mail

    def _normalize_base_user_info(self, client, extra_info, admin_ids=None):
        '''
        normalize sign in user info from MS Graph client
        '''
        user_obj = client.me.get()
        user_dict = user_obj.to_dict()
        user_info = {}
        user_info['isauthenticated'] = True
        user_info['uid'] = user_dict['id']
        user_info['mail'] = self._assign_mail(user_dict)
        user_info['photo'] = '/Photo/UserPhoto/%s' % user_dict['id']
        user_info['display_name'] = self._assign_full_name(user_dict)
        user_info['first_name'] = user_dict['givenName']
        user_info['last_name'] = user_dict['surname']
        user_info['role'] = self._check_role(user_dict['id'], admin_ids, extra_info.get('sku_ids'))
        user_info['isadmin'] = self._check_admin(user_info['role'])
        user_info['isstudent'] = self._check_student(user_info['role'])
        user_info['school_uid'] = extra_info.get('school_uid')
        user_info['school_id'] = extra_info.get('school_id')
        return user_info

    def get_current_user(self, token, ms_token):
        admin_ids = self._aad_api_service.get_admin_ids(token)
        extra_info = self._aad_api_service.get_user_extra_info(token)
        ms_client = self._ms_api_service.get_client(ms_token)
        user = self._normalize_base_user_info(ms_client, extra_info, admin_ids)
        return user

    def get_photo(self, token, user_object_id):
        photo = self._ms_api_service.get_user_photo(token, user_object_id)
        return photo
