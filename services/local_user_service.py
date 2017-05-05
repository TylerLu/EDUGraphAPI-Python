'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from account.models import LocalUser, ClassroomSeatingArrangements, UserRoles, Organizations, TokenCache

from django.contrib.auth.models import User
from services.models import O365User

class LocalUserService(object):

    def __init__(self):
        pass

    def check_login(self, data):
        result = False
        try:
            email = data['Email']
            password = data['Password']
            user = User.objects.get(username=email)
            if password == user.password and user.o365UserId and len(user.o365UserId.strip()) > 0:
                result = True
        except:
            pass
        return result

    def register(self, email, password, favorite_color):
        try:
            user = User.objects.create(username=email)
            user.set_password(password)
            user.email = email
            user.save()
            local = LocalUser(user=user, favoriteColor=favorite_color)
            local.save()
            return user
        except:
            return None

    def create_organization(self, tenant_id, tenant_name):
        organization = Organizations.objects.get_or_create(tenantId=tenant_id)[0]
        organization.name = tenant_name
        #organization.isAdminConsented = True
        organization.save()

    def update_organization(self, user_info, label):
        organization = Organizations.objects.filter(tenantId=user_info['tenant_id'])
        if organization:
            organization.update(isAdminConsented=label)

    def check_admin(self, user_info):
        user_info['is_admin_consented'] = False
        organization = Organizations.objects.filter(tenantId=user_info['tenant_id'])
        if organization:
            user_info['is_admin_consented'] = organization[0].isAdminConsented

    def get_user_by_o365_email(self, o365_email):
        local_user = LocalUser.objects.filter(o365Email=o365_email).first()
        if not local_user:
            return None
        return User.objects.filter(id=local_user.id).first()


    def get_o365_user(self, user):
        local_user = LocalUser.objects.filter(id=user.id).first()
        if local_user:
            display_name = '%s %s' % (user.first_name, user.last_name)
            # TODO: get roles and tenant name
            roles = []
            tenant_id =''
            tenant_name = ''
            return O365User(user.id, local_user.o365Email, user.first_name, user.last_name, display_name, tenant_id, tenant_name, roles)
        return None

    # def check_link_status(self, user_info):
    #     user_info['are_linked'] = False
    #     user_info['local_existed'] = False
    #     user_info['local_message'] = ''

    #     o365_user_id = user_info['uid']
    #     o365_user_mail = user_info['mail']
    #     local_user = LocalUser.objects.filter(o365UserId=o365_user_id)
    #     local_mail = User.objects.filter(username=o365_user_mail)
    #     if local_user:
    #         user_obj = local_user[0]
    #         if user_obj.o365UserId and user_obj.o365Email and user_obj.user.username:
    #             user_info['are_linked'] = True
    #             user_info['email'] = user_obj.user.username
    #             user_info['o365Email'] = user_obj.o365Email
    #     elif local_mail:
    #         user_info['local_existed'] = True
    #         user_info['local_message'] = 'There is a local account: %s matching your O365 account.' % o365_user_mail
    #     else:
    #         pass

    def get_user(self, username):
        user_info = {}
        try:
            user = User.objects.get(username=username)
            user_info['is_authenticated'] = True
            user_info['is_local'] = True
            user_info['uid'] = user.localuser.o365UserId
            user_info['mail'] = user.localuser.o365Email
            user_info['first_name'] = user.first_name
            user_info['last_name'] = user.last_name
            user_info['display_name'] = user.localuser.o365Email
            role = UserRoles.objects.get(o365UserId=user.localuser.o365UserId)
            user_info['role'] = role.name
            if user_info['role'] != 'Admin':
                user_info['is_admin'] = False
            if user_info['role'] != 'Student':
                user_info['is_student'] = False
        except:
            pass
        return user_info

    def update_role(self, uid, role_name):
         role = UserRoles.objects.get_or_create(o365UserId=uid)[0]
         role.name = role_name
         role.save()

    def create(self, user_info):
        result = True
        organization_obj = Organizations.objects.get(tenantId=user_info['tenant_id'])
        try:
            first_name = user_info['first_name']
            last_name = user_info['last_name']
            email = user_info['mail']
            password = ''
            o365_user_mail = user_info['mail']
            o365_user_id = user_info['uid']
            color = user_info['color']
            user = User.objects.get_or_create(username=email)[0]
            user.set_password(password)
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            local = LocalUser(user=user)
            local.o365UserId = o365_user_id
            local.o365Email = o365_user_mail
            local.favoriteColor = color
            local.organization_id = organization_obj.id
            local.save()
        except Exception as e:
            print(e)
            result = False
        return result

    def link(self, user_info, data):
        ret = True
        organization_obj = Organizations.objects.get(tenantId=user_info['tenant_id'])
        local_mail = data['Email']
        first_name = user_info['first_name']
        last_name = user_info['last_name']
        o365_user_mail = user_info['mail']
        o365_user_id = user_info['uid']
        user = User.objects.get(username=local_mail)
        if hasattr(user, 'localuser') and user.localuser.o365UserId:
            ret = False
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            local = LocalUser.objects.get_or_create(user=user)[0]
            local.o365UserId = o365_user_id
            local.o365Email = o365_user_mail
            local.organization_id = organization_obj.id
            local.save()
        return ret

    def link_o365(self, local_user, o365_user):
        ret = True
        organization_obj = Organizations.objects.get(tenantId=o365_user['tenant_id'])
        local_mail = local_user['mail']
        first_name = o365_user['first_name']
        last_name = o365_user['last_name']
        o365_user_mail = o365_user['mail']
        o365_user_id = o365_user['uid']
        user = User.objects.get(username=local_mail)
        if hasattr(user, 'localuser') and user.localuser.o365UserId:
            ret = False
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            local = LocalUser.objects.get_or_create(user=user)[0]
            local.o365UserId = o365_user_id
            local.o365Email = o365_user_mail
            local.organization_id = organization_obj.id
            local.save()
        return ret

    def get_color(self, user_info):
        color = ''
        try:
            color = LocalUser.objects.get(o365Email=user_info['mail']).favoriteColor
        except:
            pass
        return color

    def update_color(self, color, user_info):
        local = LocalUser.objects.filter(o365Email=user_info['mail'])
        if local:
            local = local[0]
            local.favoriteColor = color
            local.save()

    def get_positions(self, students, class_id):
        for student in students:
            position = 0
            try:
                seat_obj = ClassroomSeatingArrangements.objects.get(userId=student['uid'], classId=class_id)
                position = seat_obj.position
            except:
                pass
            student['position'] = position

    def get_colors(self, students):
        for student in students:
            color = ''
            try:
                user_obj = LocalUser.objects.get(o365UserId=student['uid'])
                color = user_obj.favoriteColor
            except:
                pass
            student['color'] = color

    def update_positions(self, seat_arrangements):
        for seat in seat_arrangements:
            user_id = seat['O365UserId']
            position = seat['Position']
            class_id = seat['ClassId']
            seat_obj = ClassroomSeatingArrangements.objects.filter(userId=user_id, classId=class_id)
            if seat_obj:
                if int(position) != 0:
                    seat_obj.update(position=position)
                else:
                    seat_obj.delete()
            else:
                if int(position) != 0:
                    ClassroomSeatingArrangements.objects.create(userId=user_id, classId=class_id, position=position)

    def get_link(self, link_id):
        local = LocalUser.objects.filter(id=link_id)
        email = ''
        o365Email = ''
        if local:
            email = local[0].user.username
            o365Email = local[0].o365Email
        return email, o365Email

    def get_links(self, tenant_id):
        organization_obj = Organizations.objects.get(tenantId=tenant_id)
        links = []
        links_obj = LocalUser.objects.filter(organization_id=organization_obj.id)
        for link in links_obj:
            if link.user.email and link.o365Email:
                record = {}
                record['id'] = link.id
                record['email'] = link.user.username
                record['o365Email'] = link.o365Email
                links.append(record)
        return links

    def remove_link(self, link_id):
        local = LocalUser.objects.filter(id=link_id)
        if local:
            o365_user_id = local[0].o365UserId
            local.update(o365UserId='', o365Email='', organization_id='')
            UserRoles.objects.filter(o365UserId=o365_user_id).delete()

    def remove_links(self, tenant_id):
        org_obj = Organizations.objects.filter(tenantId=tenant_id)
        if org_obj:
            org = org_obj[0]
            local = LocalUser.objects.filter(organization_id=org.id)
            for item in local:
                o365_user_id = item.o365UserId
                UserRoles.objects.filter(o365UserId=o365_user_id).delete()
            local.update(o365UserId='', o365Email='', organization_id='')
