import json
import requests
from urllib.parse import urlencode

class GraphServiceClient(object):

    def __init__(self, base_url, access_token):
        self._base_url = base_url
        self._access_token = access_token

    def get_users_delta(self, query_dict={}):
        url = self._base_url + '/v1.0/users/delta?' + urlencode(query_dict)
        return self.get_users(url)

    def get_users(self, absolute_url):        
        res = self._http_get_json(absolute_url)
        return res['value'], res.get('@odata.nextLink'), res.get('@odata.deltaLink')

    def _http_get_json(self, absolute_url):
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer {0}'.format(self._access_token) }
        response = requests.get(absolute_url, headers=headers)
        return json.loads(response.text)