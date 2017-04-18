"""
demo helper
"""
import json

class DemoHelper(object):
    def __init__(self):
        with open('utils/demo-pages.json') as jsonfile:
            self.data = json.load(jsonfile)

    def get_links(self, path):
        links = []
        for helper in self.data:
            if helper['path'] == path:
                links = helper['links']
                break
        return links
