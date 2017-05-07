'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''

from django.conf import settings
from django.shortcuts import render as django_render

def render(request, template_name, context=None, content_type=None, status=None, using=None):
    if context:
        if 'Message' in request.session:            
            import pdb; pdb.set_trace()
            context['message'] = request.session['Message'].split('\r\n')
            request.session['Message'] = ''
        if 'Error' in request.session:
            context['error'] = request.session['Error'].split('\r\n')
            request.session['Error'] = ''        
        context['demo_helper_links'] = settings.DEMO_HELPER.get_links(request.get_full_path())
    return django_render(request, template_name, context, content_type, status, using)