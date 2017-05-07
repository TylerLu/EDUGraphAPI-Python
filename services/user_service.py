'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from django.contrib.auth.models import User

from services.models import O365User
from account.models import Profile, ClassroomSeatingArrangements, UserRoles, Organizations, TokenCache

class UserService(object):

    def __init__(self):
        pass

    def register(self, email, password, favorite_color):
        try:
            user = User.objects.create(username=email)
            user.set_password(password)
            user.email = email
            user.profile.favoriteColor = favorite_color
            user.save()
            return user
        except Exception as e:
            print(e)
            return None

    def create(self, o365_user):  #favorite_color
        user = User.objects.get_or_create(email=o365_user.email)[0]
        user.set_password('')
        user.username = o365_user.email
        user.email = o365_user.email
        user.first_name = o365_user.first_name
        user.last_name = o365_user.last_name
        user.save()
        return user

    def create_or_update_organization(self, tenant_id, tenant_name):
        organization = Organizations.objects.get_or_create(tenantId=tenant_id)[0]
        organization.tenant_id = tenant_id
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

    def get_user_by_email(self, email):
        return User.objects.filter(email=email).first()

    def get_o365_user(self, user):
        profile = Profile.objects.filter(id=user.id).first()
        if profile:
            display_name = '%s %s' % (user.first_name, user.last_name)
            roles = self.get_roles(profile.o365UserId)
            tenant_id = profile.organization.tenantId
            tenant_name = profile.organization.name
            return O365User(user.id, profile.o365Email, user.first_name, user.last_name, display_name, tenant_id, tenant_name, roles)
        return None

    def get_user(self, id):
        return User.objects.filter(id=id).first()

    def get_roles(self, uid):
        users = UserRoles.objects.filter(o365UserId=uid)
        if users:
            roles = []
            for user in users:
                roles.append(user.name)
            return roles
        return None

    def update_role(self, uid, role_name):
         role = UserRoles.objects.get_or_create(o365UserId=uid)[0]
         role.name = role_name
         role.save()

    def get_favorite_color(self, user_id):
        profile = Profile.objects.filter(user_id=user_id).first()
        if profile:
            return profile.favoriteColor
        return None

    def get_favorite_color_by_o365_user_id(self, o365_user_id):
        profile = Profile.objects.filter(o365UserId=o365_user_id).first()
        if profile:
            return profile.favoriteColor
        return None

    def update_favorite_color(self, color, user_id):
        profile = Profile.objects.filter(user_id=user_id).first()
        if profile:
            profile.favoriteColor = color
            profile.save()

    def get_seating_position(self, o365_user_id, class_id):
        arrangement = ClassroomSeatingArrangements.objects.filter(userId=o365_user_id, classId=class_id).first()
        if arrangement:
               return arrangement.position
        return None

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
