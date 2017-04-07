from django import forms

class UserInfo(forms.Form):
    '''
    user sign in form
    '''
    Email = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control logincontrol', 'data-val':'true', 'data-val-email':'The Email field is not a valid e-mail address.', 'data-val-required':'The Email field is required.', 'id':'Email', 'placeholder':'Email', 'value':''}), required=False)
    Password = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control logincontrol', 'data-val':'true', 'data-val-required':'The Password field is required.', 'id':'Password', 'placeholder':'Password', 'type':'password'}), required=False)

class UserRegInfo(forms.Form):
    '''
    user registe form
    '''
    Email = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'data-val':'true', 'data-val-email':'The Email field is not a valid e-mail address.', 'data-val-required':'The Email field is required.', 'id':'Email', 'value':''}), required=False)
    Password = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'data-val':'true', 'data-val-length':'The Password must be at least 6 characters long.', 'data-val-length-max':'100', 'data-val-length-min':'6', 'data-val-required':'The Password field is required.', 'id':'Password', 'name':'Password', 'type':'password'}), required=False)
    ConfirmPassword = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'data-val':'true', 'data-val-equalto':'The password and confirmation password do not match.', 'data-val-equalto-other':'*.Password', 'id':'ConfirmPassword', 'type':'password'}), required=False)
    color_choices = [('#2F19FF', 'Blue'), ('#127605', 'Green'), ('#535353', 'Grey')]
    FavoriteColor = forms.CharField(widget=forms.Select(choices=color_choices, attrs={'class':'form-control', 'id':'FavoriteColor'}))
