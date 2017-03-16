from django import forms
from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'account/login.html')

def register(request):
    return render(request, 'account/register.html')

class LoginForm(forms.Form):
    style = 'form-control logincontrol'
    email = forms.EmailField(widget = forms.TextInput(attrs={'class':style, 'name':'email'}),
                             required=False, 
                             error_messages={'required': 'The Email field is required'})
    pwd = forms.CharField(required=True, 
                          error_messages={'required': 'The Email field is required'})

def login(request):
    if request.method == "POST":
        loginPost = LoginForm(request.POST)
        ret = loginPost.is_valid()
        if ret:
            pass
        else:
            return render(request, 'account/login.html',{'error': loginPost.errors, 'form': loginPost})
    else:
        objGet = LoginForm()
        return render(request, 'account/login.html',{'obj1': objGet})

def schools(request):
    userid = '13003'
    userschoolid = 1
    schools = [{'name': 'Contoso High School', 'id': 1, 'principalname': 'Amy Roebuck', 'lowestgrade': 9, 'highestgrade': 12, 'address': '2 Microsoft Way', 'city': 'Redmond', 'state': 'WA', 'zip': '98052', 'latitude': 116.67, 'longitude': 39.92},
               {'name': 'Contoso High School', 'id': 2, 'principalname': 'Amy Roebuck', 'lowestgrade': 9, 'highestgrade': 12, 'address': '2 Microsoft Way', 'city': 'Redmond', 'state': 'WA', 'zip': '98052', 'latitude': 116.67, 'longitude': 39.92}]
    isstudent = True
    isInAschool = True
    isadmin = False
    isauthenticated = True
    role = 'Student'
    username = 'Bob Jones'
    parameter_dict = {'userid': userid,
                      'isstudent': isstudent,
                      'userschoolid': userschoolid,
                      'schools': schools,
                      'isInAschool': isInAschool,
                      'isadmin': isadmin,
                      'isauthenticated': isauthenticated,
                      'role': role,
                      'username': username}
    return render(request, 'schools/index.html', parameter_dict)

def classes(request):
    role = 'Student'
    username = 'Bob Jones'
    isauthenticated = True
    isInAschool = True
    schoolname = 'Contoso High School'
    principalname = 'Amy Roebuck'
    lowestgrade = 9
    highestgrade = 12
    isstudent = True
    sections = [{'displayname':'Test Email Gen 2', 'combinedcoursenumber': 'TES409', 'courseId': '11018409', 'coursedescription': 'Test Email Gen 2', 'teachers': [{'displayname':'abc'}], 'termname': 'SY1516', 'termstartdate': '2015-09-01T00:00:00', 'termenddate': '2016-06-15T00:00:00', 'period': 3}]
    mysections = [{'displayname':'Test Email', 'combinedcoursenumber': 'TES333', 'courseId': '1111111', 'coursedescription': 'Test Email Gen 2', 'teachers': [{'displayname':'abc'}], 'termname': 'SY1516', 'termstartdate': '2015-09-01T00:00:00', 'termenddate': '2016-06-15T00:00:00', 'period': 3}]
    sectionsnextlink = '/Schools'
    parameter_dict = {'role': role,
                      'username': username,
                      'isInAschool': isInAschool,
                      'isauthenticated': isauthenticated,
                      'schoolname': schoolname,
                      'principalname': principalname,
                      'lowestgrade': lowestgrade,
                      'highestgrade': highestgrade,
                      'isstudent': isstudent,
                      'sections': sections,
                      'mysections': mysections,
                      'sectionsnextlink': sectionsnextlink}
    return render(request, 'schools/classes.html', parameter_dict)

def users(request):
    role = 'Student'
    username = 'Bob Jones'
    isauthenticated = True
    isInAschool = True
    isstudent = True
    schoolname = 'Contoso High School'
    principalname = 'Amy Roebuck'
    lowestgrade = 9
    highestgrade = 12
    users = [{'displayname': '001test', 'type': 'teacher'},
             {'displayname': '002test', 'type': 'student'}]
    students = [{'displayname': '001test', 'type': 'student'},
             {'displayname': '002test', 'type': 'student'}]
    teachers = [{'displayname': '001test', 'type': 'teacher'},
             {'displayname': '002test', 'type': 'teacher'}]
    parameter_dict = {'role': role,
                      'username': username,
                      'isInAschool': isInAschool,
                      'isauthenticated': isauthenticated,
                      'schoolname': schoolname,
                      'principalname': principalname,
                      'lowestgrade': lowestgrade,
                      'highestgrade': highestgrade,
                      'users': users,
                      'students': students,
                      'teachers': teachers}
    return render(request, 'schools/users.html', parameter_dict)

def classdetails(request):
    role = 'Student'
    username = 'Bob Jones'
    isauthenticated = True
    isInAschool = True
    isstudent = False
    schoolname = 'Contoso High School'
    coursename = 'Health 305'
    coursenumber = '305'
    displayname = 'Health 3B'
    section = {'coursename': 'Health 305', 'coursenumber': '305', 'displayname': 'Health 3B', 'coursedesc': 'Health 3B', 'period': 8, 'termname': 'SY1516', 'termstartdate': 'September 1 2015', 'termenddate': 'June 15 2016', 'teachers': ['George Martin', 'George Martin', 'George Martin'], 'students': [{'displayname':'001', 'educationgrade':1}, {'displayname':'002', 'educationgrade':3}]}
    driveitems = [{'url':'','name':'test001','lastmodifieddatetime':'11/21/2016 03: 00: 17 PM','lastusername':'abc'}, 
                  {'url':'','name':'test002','lastmodifieddatetime':'11/21/2016 03: 00: 17 PM','lastusername':'abc'}]
    conversations = [{'topic':'aaaaa'}, {'topic':'bbbb'}]
    seatrange = range(1, 37)
    parameter_dict = {'role': role,
                      'username': username,
                      'isstudent': isstudent,
                      'isInAschool': isInAschool,
                      'isauthenticated': isauthenticated,
                      'schoolname': schoolname,
                      'section': section,
                      'driveitems': driveitems,
                      'conversations': conversations,
                      'seatrange': seatrange}
    return render(request, 'schools/classdetails.html', parameter_dict)

def aboutme(request):
    username = 'test001'
    isauthenticated = True
    userrole = 'student'
    showcolor = True
    groups = ['test001', 'test002', 'test003']
    parameter_dict = {'username':username,
                      'isauthenticated': isauthenticated,
                      'userrole': userrole,
                      'showcolor': showcolor,
                      'groups': groups}
    return render(request, 'manage/aboutme.html', parameter_dict)

def link(request):
    username = 'test001'
    isauthenticated = True
    arelinked = True
    islocal = False
    localexisted = True
    localmessage = "There is a local account: test@test.com matching your O365 account."
    user = {'email':'123@456.com', 'o365email': 'office@office.com'}
    parameter_dict = {'username':username,
                      'isauthenticated': isauthenticated,
                      'arelinked': arelinked,
                      'islocal': islocal,
                      'localexisted': localexisted,
                      'localmessage': localmessage,
                      'user': user}
    return render(request, 'manage/link.html', parameter_dict)

    
