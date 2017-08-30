'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''

import constant
from django.conf import settings
from django.shortcuts import render as django_render

def render(request, template_name, context=None, content_type=None, status=None, using=None):
    if context:
        if 'Message' in request.session:
            context['message'] = request.session['Message'].split('\r\n')
            del request.session['Message']
        if 'Error' in request.session:
            context['error'] = request.session['Error'].split('\r\n')
            del request.session['Error']      
        source_code_repository_url = constant.source_code_repository_url
        if not source_code_repository_url.endswith('/'):
            source_code_repository_url = source_code_repository_url + '/'
        context['source_code_repository_url'] = source_code_repository_url        
        context['demo_helper_functions'] = settings.DEMO_HELPER.get_functions(request.get_full_path())
    return django_render(request, template_name, context, content_type, status, using)