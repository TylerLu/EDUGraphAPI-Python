'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
import re
import json

class DemoHelper(object):
    def __init__(self):
        with open('utils/demo-pages.json') as jsonfile:
            self.data = json.load(jsonfile)
        self.path_links = self._convert()
        self._object_id_filter = re.compile('\w+-\w+-\w+-\w+-\w+')
        self._number_filter = re.compile('\d+')
        
    def get_links(self, path):
        links = []
        if path not in self.path_links:
            path = self._filter_path(path)
        if path in self.path_links:
            links = self.path_links[path]
        return links

    def _convert(self):
        result = {}
        if self.data:
            for item in self.data:
                result[item['path']] = item['links']
        return result

    def _filter_path(self, path):
        new_path = re.sub(self._object_id_filter, '', path)
        new_path = re.sub(self._number_filter, '', new_path)
        return new_path