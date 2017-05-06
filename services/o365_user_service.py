'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from constant import Roles
from constant import O365ProductLicenses
from services.models import O365User
from services.ms_graph_service import MSGraphService
from services.aad_graph_service import AADGraphService

class O365UserService(object):

    def __init__(self, tenant_id, ms_graph_access_token, aad_graph_service_access_token):
        self._tenant_id = tenant_id
        self._ms_graph_service = MSGraphService(ms_graph_access_token)
        self._aad_graph_service = AADGraphService(self._tenant_id, aad_graph_service_access_token)

    def get_o365_user(self):
        me = self._ms_graph_service.get_me().to_dict()
        org = self._ms_graph_service.get_organization(self._tenant_id)

        id = me['id']
        first_name = me['givenName']
        last_name = me['surname']
        display_name = me['displayName']
        email = me['mail']
        if not email:
            email = me['userPrincipalName']
        tenant_name = org['displayName']
        roles = self._get_roles(id)
        photo = '/Photo/UserPhoto/' + id
        return O365User(id, email, first_name, last_name, display_name, self._tenant_id, tenant_name, roles, photo)

    def _get_roles(self, user_id):
        roles = []
        admin_ids = self._aad_graph_service.get_admin_ids()
        if user_id in admin_ids:
            roles.append('Admin')
        license_ids = self._aad_graph_service.get_license_ids()
        for license_id in license_ids:
            if license_id == O365ProductLicenses.Faculty or license_id == O365ProductLicenses.FacultyPro:
                roles.append(Roles.Faculty)
            if license_id == O365ProductLicenses.Student or license_id == O365ProductLicenses.StudentPro:
                roles.append(Roles.Student)
        return roles
