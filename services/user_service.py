'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
from account.models import LocalUser, ClassroomSeatingArrangements, UserRoles

from django.contrib.auth.models import User

class LocalUserService(object):
    
    def __init__(self):
        pass
    
    def check_login(self, data):
        result = False
        try:
            email = data['Email']
            password = data['Password']
            user = User.objects.get(email=email)
            if password == user.password and user.o365UserId and len(user.o365UserId.strip()) > 0:
                result = True
        except:
            pass
        return result

    def register(self, data):
        email = data['Email']
        password = data['Password']
        favoriteColor = data['FavoriteColor']
        ret = True
        try:
            user = User.objects.create(username=email)
            user.set_password(password)
            user.email = email
            user.save()
            local = LocalUser(user=user, favoriteColor=favoriteColor)
            local.save()
        except:
            ret = False
        return ret

    def check_link_status(self, user_info):
        user_info['arelinked'] = False
        user_info['localexisted'] = False
        user_info['localmessage'] = ''

        o365_user_id = user_info['uid']
        o365_user_mail = user_info['mail']
        local_user = LocalUser.objects.filter(o365UserId=o365_user_id)
        local_mail = User.objects.filter(username=o365_user_mail)
        if local_user:
            user_obj = local_user[0]
            if user_obj.o365UserId and user_obj.o365Email and user_obj.user.email:
                user_info['arelinked'] = True
                user_info['email'] = user_obj.user.email
                user_info['o365Email'] = user_obj.o365Email
        elif local_mail:
            user_info['localexisted'] = True
            user_info['localmessage'] = 'There is a local account: %s matching your O365 account.' % o365_user_mail
        else:
            pass
    
    def get_user(self, username):
        user_info = {}
        try:
            user = User.objects.get(username=username)
            user_info['isauthenticated'] = True
            user_info['islocal'] = True
            user_info['uid'] = user.localuser.o365UserId
            user_info['mail'] = user.localuser.o365Email
            user_info['first_name'] = user.first_name
            user_info['last_name'] = user.last_name
            user_info['display_name'] = user.localuser.o365Email 
            role = UserRoles.objects.get(o365UserId=user.localuser.o365UserId)
            user_info['role'] = role.name
            if user_info['role'] != 'Admin':
                user_info['isadmin'] = False
            if user_info['role'] != 'Student':
                user_info['isstudent'] = False
        except:
            pass
        return user_info
    
    def update_role(self, uid, role_name):
         role = UserRoles.objects.get_or_create(o365UserId=uid)[0]
         role.name = role_name
         role.save()

    def create(self, user_info):
        result = True
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
            local.save()
        except Exception as e:
            print(e)
            result = False
        return result
    
    def link(self, user_info, data):
        local_mail = data['Email']
        password = data['Password']
        first_name = user_info['first_name']
        last_name = user_info['last_name']
        o365_user_mail = user_info['mail']
        o365_user_id = user_info['uid']
        user = User.objects.get(username=local_mail)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        local = LocalUser(user=user)
        local.o365UserId = o365_user_id
        local.o365Email = o365_user_mail
        local.save()

    def get_color(self, user_info):
        color = ''
        try:
            color = LocalUser.objects.get(o365Email=user_info['mail']).favoriteColor
        except:
            pass
        return color

    def update_color(self, color, user_info):
        local = LocalUser.objects.filter(o365Email=user_info['mail'])[0]
        if local:
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
    
    def get_links(self):
        links = []
        links_obj = LocalUser.objects.all()
        for link in links_obj:
            if link.user.email and link.o365Email:
                record = {}
                record['id'] = link.id
                record['email'] = link.user.email
                record['o365Email'] = link.o365Email
                links.append(record)
        return links
    
    def remove_link(self, link_id):
        local = LocalUser.objects.filter(id=link_id)
        email = ''
        if local:
            email = local[0].user.email
        LocalUser.objects.filter(id=link_id).delete()
        if email:
            User.objects.filter(email=email).delete()
