'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import re
import json
import requests
import constant

class HttpRequestFailed(Exception):
    def __init__(self, request, response):
        self._request = request
        self._response = response

    @property
    def response(self):
        return self._request

    @property
    def response(self):
        return self._response

class RestApiService(object):

    def get_raw(self, url, token, headers=None):
        method = 'GET'
        s_headers = {}
        self._set_header_token(s_headers, token)
        if headers:
            s_headers.update(headers)
        response = self._send(method, url, s_headers)
        return response.text

    def get_json(self, url, token, headers=None):
        method = 'GET'
        s_headers = {'Accept': 'application/json',
                     'Content-Type': 'application/json'}
        self._set_header_token(s_headers, token)
        if headers:
            s_headers.update(headers)
        response = self._send(method, url, s_headers)
        return json.loads(response.text)

    def get_img(self, url, token, headers=None):
        method = 'GET'
        s_headers = {'content-type': 'image/jpeg'}
        self._set_header_token(s_headers, token)
        if headers:
            s_headers.update(headers)
        response = self._send(method, url, s_headers)
        return response.content

    def get_object_list(self, url, token, key='value', headers=None, model=None, next_key=''):
        content = self.get_json(url, token, headers)
        entity_list = []
        next_link = ''
        if content and model:
            value_list = content[key]
            for value in value_list:
                entity = model(value)
                entity_list.append(entity)
            if next_key:
                next_link = content.get(next_key, '')
        if next_key:
            return entity_list, next_link
        else:
            return entity_list

    def get_object(self, url, token, headers=None, model=None):
        content = self.get_raw(url, token, headers)
        if content and model:
            value = json.loads(content)
            return model(value)
        return None

    def delete(self, url, token, headers=None):
        method = 'DELETE'
        s_headers = {'Accept': 'application/json',
                     'Content-Type': 'application/json'}
        self._set_header_token(s_headers, token)
        if headers:
            s_headers.update(headers)
        self._send(method, url, s_headers)

    def post_json(self, url, token, headers=None, data=None):
        method = 'POST'
        s_headers = {'Accept': 'application/json',
                     'Content-Type': 'application/json'}
        self._set_header_token(s_headers, token)
        if headers:
            s_headers.update(headers)
        return self._send(method, url, s_headers, json.dumps(data))

    def put_file(self, url, token, file=None):      
        s_headers = {'Content-Type': 'application/octet-stream'}        
        self._set_header_token(s_headers, token)
        method = 'PUT'
        return json.loads(self._send(method, url, s_headers,file.chunks()).text)

    def _set_header_token(self, headers, token):
        key = 'Authorization'
        value = 'Bearer {0}'.format(token)
        headers[key] = value

    def _send(self, method, url, headers, data=None):
        session = requests.Session()
        request = requests.Request(method, url, headers, data=data)
        prepped = request.prepare()
        response = session.send(prepped)
        if response.status_code < 200 or response.status_code > 299:
            raise HttpRequestFailed(request, response)
        return response
 