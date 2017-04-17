from django.http import HttpResponseRedirect

def ms_login_required(func):  
    def wrapper(request, *args, **kwargs):
        if not request.session['ms_user'] or not request.session['aad_token'] or not request.session['ms_token']:
            return HttpResponseRedirect('/Account/Login')
        else:
            return func(request)
    return wrapper  
 
