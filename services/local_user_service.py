'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from django.contrib.auth.models import User

from services.models import O365User
from account.models import Profile, ClassroomSeatingArrangements, UserRoles, Organizations, TokenCache

class LocalUserService(object):

    def __init__(self):
        pass

    def register(self, email, password, favorite_color):
        try:
            user = User.objects.create(username=email)
            user.set_password(password)
            user.email = email
            user.profile.favoriteColor - favoriteColor
            user.save()
            return user
        except Exception as e:
            print(e)
            return None

    def create_organization(self, tenant_id, tenant_name):
        organization = Organizations.objects.get_or_create(tenantId=tenant_id)[0]
        organization.name = tenant_name
        organization.save()

    def update_organization(self, tenant_id, is_admin_consented):
        organization = Organizations.objects.filter(tenantId=tenant_id)
        if organization:
            organization.update(isAdminConsented=is_admin_consented)

    def is_tenant_consented(self, tenant_id):
        org = Organizations.objects.filter(tenantId=tenant_id).first()
        return org is not None and org.isAdminConsented

    def get_user_by_o365_email(self, o365_email):
        profile = Profile.objects.filter(o365Email=o365_email).first()
        if not profile:
            return None
        return User.objects.filter(id=profile.id).first()

    def get_o365_user(self, user):
        profile = Profile.objects.filter(id=user.id).first()
        if profile:
            display_name = '%s %s' % (user.first_name, user.last_name)
            # TODO: get roles
            roles = [ 'Admin' ]
            tenant_id =user.organization.tenantId
            tenant_name = user.organization.name
            return O365User(user.id, profile.o365Email, user.first_name, user.last_name, display_name, tenant_id, tenant_name, roles)
        return None

    def get_user_by_email(email):
        return User.objects.filter(email=email).first()

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
            user_info['uid'] = user.profile.o365UserId
            user_info['mail'] = user.profile.o365Email
            user_info['first_name'] = user.first_name
            user_info['last_name'] = user.last_name
            user_info['display_name'] = user.profile.o365Email
            role = UserRoles.objects.get(o365UserId=user.profile.o365UserId)
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

    def create(self, o365_user):  #favorite_color
        user = User.objects.get_or_create(email=o365_user.email)[0]
        user.set_password('')
        user.username = o365_user.email
        user.email = o365_user.email
        user.first_name = o365_user.first_name
        user.last_name = o365_user.last_name
        user.save()
        return user

    def link(self, local_user, o365_user, favorite_color):
        org = Organizations.objects.get_or_create(tenantId=o365_user.tenant_id)[0]
        org.tenantId = o365_user.tenant_id
        org.name = o365_user.tenant_name
        org.save()

        link = Profile.objects.get_or_create(user_id=local_user.id)[0]
        link.o365UserId = o365_user.id
        link.o365Email = o365_user.email
        link.favoriteColor = favorite_color
        link.organization_id = org.id
        link.save()
        return link

    def get_favorite_color(self, user_id):
        profile = Profile.objects.filter(user_id=user_id).first()
        if profile:
            return profile.favoriteColor
        return None

    def update_favorite_color(self, color, user_id):
        profile = Profile.objects.filter(user_id=user_id).first()
        if profile:
            profile.favoriteColor = color
            profile.save()

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
                profile = Profile.objects.get(o365UserId=student['uid'])
                color = profile.favoriteColor
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
        profile = Profile.objects.filter(id=link_id)
        email = ''
        o365Email = ''
        if profile:
            email = profile[0].user.username
            o365Email = profile[0].o365Email
        return email, o365Email

    def get_linked_accounts(self, tenant_id):
        organization_obj = Organizations.objects.get(tenantId=tenant_id)
        accounts = []
        profiles = Profile.objects.filter(organization_id=organization_obj.id)
        for profile in profiles:
            if profile.o365Email:
                record = {}
                record['id'] = profile.id
                record['email'] = profile.user.username
                record['o365Email'] = profile.o365Email
                accounts.append(record)
        return accounts

    def remove_link(self, link_id):
        profile = Profile.objects.filter(id=link_id)
        if profile:
            o365_user_id = profile[0].o365UserId
            profile.update(o365UserId='', o365Email='', organization_id='')
            UserRoles.objects.filter(o365UserId=o365_user_id).delete()

    def remove_links(self, tenant_id):
        org_obj = Organizations.objects.filter(tenantId=tenant_id)
        if org_obj:
            org = org_obj[0]
            profiles = Profile.objects.filter(organization_id=org.id)
            for item in profiles:
                o365_user_id = item.o365UserId
                UserRoles.objects.filter(o365UserId=o365_user_id).delete()
            profiles.update(o365UserId='', o365Email='', organization_id='')

    def is_o365_user_linked(self, o365_user_id):
        link = Profile.objects.filter(o365UserId=o365_user_id).first()
        return link is not None
