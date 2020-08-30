import os
import requests
from ansible.errors import AnsibleError

class NextcloudHandler:
    def __init__(self, kwargs):
        self.HOST = kwargs.get('host') or os.environ.get('NEXTCLOUD_HOST')
        self.USER = kwargs.get('user') or os.environ.get('NEXTCLOUD_USER')
        self.TOKEN = kwargs.get('api_token') or os.environ.get('NEXTCLOUD_TOKEN')

        if None in [self.HOST, self.USER, self.TOKEN]:
            raise AnsibleError('Unable to perform nextcloud passwords lookup. '
                                        'host, user, api_token and label are required.')
    
    def get(self, path):
        r = requests.get(
            'https://{HOST}/{PATH}'.format(HOST=self.HOST, PATH=path),
            auth=(self.USER, self.TOKEN)
        )
        return r
