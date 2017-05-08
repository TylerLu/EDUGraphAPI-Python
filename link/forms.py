'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''

from django import forms

class CreateLocalInfo(forms.Form):
    '''
    create local info
    '''
    color_choices = [('#2F19FF', 'Blue'), ('#127605', 'Green'), ('#535353', 'Grey')]
    FavoriteColor = forms.CharField(widget=forms.Select(choices=color_choices, attrs={'class':'form-control', 'id':'FavoriteColor'}))

class LoginLocalInfo(forms.Form):
    '''
    login local info
    '''
    Email = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'id':'Email', 'value':''}), required=True)
    Password = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'id':'Password', 'type':'password'}), required=True)