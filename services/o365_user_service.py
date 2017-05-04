'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from constant import Roles
from constant import O365ProductLicenses

class O365UserService(object):

    def get_client_user(self, graph_user, graph_organization, admin_ids, license_ids):
        user_info = self._normalize_client_user_info(graph_user, graph_organization)
        role = self._check_role(user_info['uid'], admin_ids, license_ids)
        user_info['role'] = role
        user_info['is_authenticated'] = True
        user_info['is_admin'] = role == 'Admin'
        user_info['is_student'] = role == 'Student'
        return user_info

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

    def _assign_full_name(self, user_dict):
        given_name = user_dict['givenName'].strip()
        sur_name = user_dict['surname'].strip()
        if given_name and sur_name:
            full_name = given_name + ' ' + sur_name
        else:
            full_name = user_dict['displayName']
        return full_name

    def _assign_mail(self, user_dict):
        mail = ''
        if not user_dict['mail']:
            mail = user_dict['userPrincipalName']
        else:
            mail = user_dict['mail']
        return mail

    def _normalize_client_user_info(self, graph_user, graph_organization):
        '''
        normalize sign in user info from MS Graph client
        '''
        user_dict = graph_user.to_dict()
        user_info = {}
        user_info['uid'] = user_dict['id']
        user_info['mail'] = self._assign_mail(user_dict)
        user_info['photo'] = '/Photo/UserPhoto/%s' % user_dict['id']
        user_info['display_name'] = self._assign_full_name(user_dict)
        user_info['first_name'] = user_dict['givenName']
        user_info['last_name'] = user_dict['surname']
        user_info['tenant_id'] = graph_organization['id']
        user_info['tenant_name'] = graph_organization['displayName']
        return user_info
