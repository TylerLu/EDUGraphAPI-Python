import json
import constant

class O365User(object):
    def __init__(self, id=None, email=None, first_name=None, last_name=None, display_name=None, tenant_id=None, tenant_name=None, roles=None, photo=None):
        self._id = id
        self._email = email
        self._first_name = first_name
        self._last_name = last_name
        self._display_name = display_name
        self._tenant_id = tenant_id
        self._tenant_name = tenant_name
        self._roles = roles
        self._photo = photo

    @property
    def id(self):
        return self._id

    @property
    def email(self):
        return self._email

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def display_name(self):
        return self._display_name

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def tenant_name(self):
        return self._tenant_name

    @property
    def roles(self):
        return self._roles

    @property
    def photo(self):
        return self._photo

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @staticmethod
    def from_json(value):
        obj = O365User()
        obj.__dict__.update(json.loads(value))
        return obj

class UnifiedUser(object):

    def __init__(self, request):
        self._request = request
        if constant.o365_user_session_key in self._request.session:
            user_json = self._request.session[constant.o365_user_session_key]
            self._o365_user = O365User.from_json(user_json)
        else:
            self._o365_user = None

    @property
    def is_authenticated(self):
        return self.o365_user is not None or self.local_user.is_authenticated

    @property
    def are_linked(self):
        return self.o365_user is not None and self.local_user.is_authenticated

    @property
    def is_admin(self):
        return self.o365_user is not None and 'Admin' in self.o365_user.roles

    @property
    def is_teacher(self):
        return self.o365_user is not None and 'Teacher' in self.o365_user.roles

    @property
    def is_student(self):
        return self.o365_user is not None and 'Student' in self.o365_user.roles

    @property
    def email(self):
        return self.local_user.email

    @property
    def o365_email(self):
        return self.o365_user.email

    @property
    def o365_user_id(self):
        return self.o365_user.id

    @property
    def user_id(self):
        return self.local_user.id

    @property
    def tenant_id(self):
        return self.o365_user.tenant_id

    @property
    def is_local(self):
        return self.o365_user is None

    @property
    def is_o365(self):
        return not self.local_user.is_authenticated

    @property
    def display_name(self):
        user = self.o365_user
        if not user and self.local_user.is_authenticated:
            user = self.local_user
        if user:
            if user.first_name and user.last_name:
                return "%s %s" % (user.first_name, user.last_name)
            else:
                return user.email
        return ''

    @property
    def main_role(self):
        if not self.o365_user:
            return None
        roles = self.o365_user.roles
        for role in ['Admin', 'Teacher', 'Student']:
            if role in roles:
                return role
        return None

    @property
    def photo(self):
        if not self.o365_user:
            return None
        return self.o365_user.photo

    @property
    def local_user(self):
        return self._request.user

    @property
    def o365_user(self):
        return self._o365_user
