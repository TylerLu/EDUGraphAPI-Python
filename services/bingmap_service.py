'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.  
 *   * See LICENSE in the project root for license information.  
'''
import json
import requests
import urllib.parse
import constant

class BingMapService(object):
    
    def __init__(self):
        self._bing_map_key = constant.bing_map_key
        self._base_uri = 'http://dev.virtualearth.net/REST/v1/Locations/US/%s?output=json&key=' + self._bing_map_key

    def get_lat_lon(self, state, city, address):
        lat = ''
        lon = ''
        state = state
        city = urllib.parse.quote(city)
        address = urllib.parse.quote(address)
        query = '%s/%s/%s' % (state, city, address)
        query_url = self._base_uri % query
        try:
            response = requests.request('GET', query_url)
            if response.status_code == 200:
                result = json.loads(response.text)
                lat_lon_list = result['resourceSets'][0]['resources'][0]['point']['coordinates']
                lat, lon = lat_lon_list
        except:
            pass
        return lat, lon

