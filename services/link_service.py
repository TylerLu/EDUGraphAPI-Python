'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
from django.contrib.auth.models import User

from services.models import O365User
from account.models import Profile, ClassroomSeatingArrangements, UserRoles, Organizations, TokenCache

class LinkService(object):

    def __init__(self):
        pass
 
    def is_linked(self, o365_user_id):
        link = Profile.objects.filter(o365UserId=o365_user_id).first()
        return link is not None

    def link(self, local_user, o365_user):
        org = Organizations.objects.get_or_create(tenantId=o365_user.tenant_id)[0]
        org.tenantId = o365_user.tenant_id
        org.name = o365_user.tenant_name
        org.save()

        profile = Profile.objects.get_or_create(user_id=local_user.id)[0]
        profile.o365UserId = o365_user.id
        profile.o365Email = o365_user.email
        profile.organization_id = org.id
        profile.save()

    def get_link(self, link_id):        
        profile = Profile.objects.filter(id=link_id).first()
        if profile:            
            link = {}
            link['email'] = profile.user.username
            link['o365Email'] = profile.o365Email
            return link
        return None

    def get_links(self, tenant_id):
        organization_obj = Organizations.objects.get(tenantId=tenant_id)
        links = []
        profiles = Profile.objects.filter(organization_id=organization_obj.id)
        for profile in profiles:
            if profile.o365Email:
                link = {}
                link['id'] = profile.id
                link['email'] = profile.user.username
                link['o365Email'] = profile.o365Email
                links.append(link)
        return links

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

