from django import forms

class CreateLocalInfo(forms.Form):
    '''
    create local info
    '''
    color_choices = [('#2F19FF', 'Blue'), ('#127605', 'Green'), ('#535353', 'Grey')]
    FavoriteColor = forms.CharField(widget=forms.Select(choices=color_choices, attrs={'class':'form-control', 'id':'FavoriteColor'}))

