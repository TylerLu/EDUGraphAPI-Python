'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''
import re
import json
import requests
import constant

class RestApiService(object):

    def get_raw(self, url, token, headers=None):
        method = 'GET'
        s_headers = {}
        self._set_header_token(s_headers, token)
        if headers:
            s_headers.update(headers)
        response = self._send(method, url, s_headers)
        content = ''
        if response.status_code == 200:
            content = response.text
        return content

    def get_json(self, url, token, headers=None):
        method = 'GET'
        s_headers = {'Accept': 'application/json',
                     'Content-Type': 'application/json'}
        self._set_header_token(s_headers, token)
        if headers:
            s_headers.update(headers)
        response = self._send(method, url, s_headers)
        content = ''
        if response.status_code == 200:
            content = json.loads(response.text)
        return content

    def get_img(self, url, token, headers=None):
        method = 'GET'
        s_headers = {'content-type': 'image/jpeg'}
        self._set_header_token(s_headers, token)
        if headers:
            s_headers.update(headers)
        response = self._send(method, url, s_headers)
        content = ''
        if response.status_code == 200:
            content = response.content
        return content

    def get_object_list(self, url, token, key='value', headers=None, model=None, next_key=''):
        content = self.get_json(url, token, headers)
        entity_list = []
        next_link = ''
        if content and model:
            value_list = content[key]
            for value in value_list:
                entity = model(value)
                out_entity = dict((name, getattr(entity, name)) for name in dir(entity) if not name.startswith('__')  and not callable(getattr(entity, name)))
                entity_list.append(out_entity)
            if next_key:
                next_link = content.get(next_key, '')
        if next_key:
            return entity_list, next_link
        else:
            return entity_list

    def get_object(self, url, token, headers=None, model=None):
        content = self.get_raw(url, token, headers)
        out_entity = None
        if content and model:
            value = json.loads(content)
            entity = model(value)
            out_entity = dict((name, getattr(entity, name)) for name in dir(entity) if not name.startswith('__')  and not callable(getattr(entity, name)))
        return out_entity

    def _set_header_token(self, headers, token):
        key = 'Authorization'
        value = 'Bearer {0}'.format(token)
        headers[key] = value

    def _send(self, method, url, headers):
        session = requests.Session()
        request = requests.Request(method, url, headers)
        prepped = request.prepare()
        response = session.send(prepped)
        return response
