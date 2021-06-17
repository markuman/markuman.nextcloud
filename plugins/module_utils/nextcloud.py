import os
import requests
import json
from ansible.errors import AnsibleError


def status_code_error(status):
    raise AnsibleError('Nextcloud retured with status code {SC}'.format(SC = status))


class NextcloudHandler:
    def __init__(self, kwargs):
        self.HTTP = 'https'
        self.ssl = True
        if kwargs.get('ssl_mode') == 'http':
            self.HTTP = 'http'
        elif kwargs.get('ssl_mode') == 'skip':
            self.ssl = False

        self.details = kwargs.get('details') or False

        self.HOST = kwargs.get('host') or os.environ.get('NEXTCLOUD_HOST')
        if self.HOST is None:
            raise AnsibleError('Unable to continue. No Nextcloud Host is given.')

        self.USER = kwargs.get('user') or os.environ.get('NEXTCLOUD_USER')
        if self.USER is None:
            raise AnsibleError('Unable to continue. No Nextcloud User is given.')

        self.TOKEN = kwargs.get('api_token') or os.environ.get('NEXTCLOUD_TOKEN')
        if self.TOKEN is None:
            raise AnsibleError('Unable to continue. No Nextcloud Token is given.')

        self.headers = {
            'Accept': 'application/json',
            'OCS-APIRequest': 'true'
        }

    def get(self, path):
        r = requests.get(
            '{HTTP}://{HOST}/{PATH}'.format(HTTP=self.HTTP, HOST=self.HOST, PATH=path),
            auth=(self.USER, self.TOKEN), verify=self.ssl, headers=self.headers
        )

        if r.status_code == 200:
            return r
        elif r.status_code == 404:
            raise AnsibleError('File {FILE} does not exist'.format(FILE=path))
        else:
            status_code_error(r.status_code)


    def put(self, path, src):
        r = requests.put(
            '{HTTP}://{HOST}/{PATH}'.format(HTTP=self.HTTP, HOST=self.HOST, PATH=path), 
            data=open(src, 'rb'), auth=(self.USER, self.TOKEN), verify=self.ssl
        )
        
        if r.status_code in [200, 201, 204]:
            return r, True
        else:
            status_code_error(r.status_code)


    def delete(self, path):
        r = requests.delete(
            '{HTTP}://{HOST}/{PATH}'.format(HTTP=self.HTTP, HOST=self.HOST, PATH=path),
            auth=(self.USER, self.TOKEN), verify=self.ssl
        )

        if r.status_code in [200, 204]:
            return r, True
        elif r.status_code == 404:
            return r, False
        else:
            status_code_error(r.status_code)

    def talk(self, message, channel):
        body = {
            'message': message,
            'replyTo': 0
        }

        spreed_v1_path = "ocs/v2.php/apps/spreed/api/v1/chat"

        r = requests.post(
            '{HTTP}://{HOST}/{V1}/{CHANNEL}'.format(HTTP=self.HTTP, HOST=self.HOST, V1=spreed_v1_path, CHANNEL=channel), 
            data=body, 
            headers=self.headers,
            auth=(self.USER, self.TOKEN),
            verify=self.ssl
        )

        if r.status_code == 201:
            return r, True
        else:
            status_code_error(r.status_code)

    def list_passwords(self, term):
        r = self.get("index.php/apps/passwords/api/1.0/password/list")
        
        ret = []
        try:
            if r.status_code == 200:
                for item in r.json():
                    if item['label'] == term:
                        if self.details:
                            ret.append(item)
                        else:
                            ret.append(item['password'])
            else:
                status_code_error(r.status_code)
        except AnsibleParserError:
            status_code_error(r.status_code)
        return ret


    def user(self):
        return self.USER
