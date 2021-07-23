import os
import requests
import json
from ansible.errors import AnsibleError
from xml.dom import minidom


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

    def propfind(self, path):
        dios_mio = """<?xml version="1.0"?>
<d:propfind  xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">
<d:prop>
        <d:getlastmodified />
        <d:getetag />
        <d:getcontenttype />
        <d:resourcetype />
        <oc:fileid />
        <oc:permissions />
        <oc:size />
        <oc:checksums />
        <oc:favorite />
        <oc:owner-display-name />
        <oc:share-types />
</d:prop>
</d:propfind>
"""
        s = requests.Session()
        s.auth = (self.USER, self.TOKEN)
        r = s.request(method='PROPFIND',
            url='{HTTP}://{HOST}/{PATH}'.format(HTTP=self.HTTP, HOST=self.HOST, PATH=path),
            headers={'Depth': '0'},
            data=dios_mio,
            verify=self.ssl
        )

        if r.status_code == 207:
            dom = minidom.parseString(r.text.encode('ascii', 'xmlcharrefreplace'))
            try:
                return {
                    'last_modified': dom.getElementsByTagName('d:getlastmodified')[0].firstChild.data,
                    'content_type': dom.getElementsByTagName('d:getcontenttype')[0].firstChild.data,
                    'file_id': int(dom.getElementsByTagName('oc:fileid')[0].firstChild.data),
                    'size': int(dom.getElementsByTagName('oc:size')[0].firstChild.data),
                    'favorite': int(dom.getElementsByTagName('oc:favorite')[0].firstChild.data),
                    'owner': dom.getElementsByTagName('oc:owner-display-name')[0].firstChild.data,
                    'href': dom.getElementsByTagName('d:href')[0].firstChild.data
                }
            except:
                # I guess it's folder, because it has no content_type
                return {
                    'last_modified': dom.getElementsByTagName('d:getlastmodified')[0].firstChild.data,
                    'content_type': 'inode/directory',
                    'file_id': dom.getElementsByTagName('oc:fileid')[0].firstChild.data,
                    'size': dom.getElementsByTagName('oc:size')[0].firstChild.data,
                    'favorite': dom.getElementsByTagName('oc:favorite')[0].firstChild.data,
                    'owner': dom.getElementsByTagName('oc:owner-display-name')[0].firstChild.data,
                    'href': dom.getElementsByTagName('d:href')[0].firstChild.data
                }

        elif r.status_code == 404:
            return {}

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

    def list_passwords(self):
        r = self.get("index.php/apps/passwords/api/1.0/password/list")
        if r.status_code == 200:
            return r.json()     
        else:
            status_code_error(r.status_code)

    def list_passwords_folders(self):
        r = self.get("index.php/apps/passwords/api/1.0/folder/list")
        if r.status_code == 200:
            return r.json()
        else:
            status_code_error(r.status_code)


    def create_passwords_folder(self, name):
        post_obj = {
            'label': name
        }

        r = requests.post(
            '{HTTP}://{HOST}/index.php/apps/passwords/api/1.0/folder/create'.format(HTTP=self.HTTP, HOST=self.HOST),
            data=post_obj,
            headers=self.headers,
            auth=(self.USER, self.TOKEN),
            verify=self.ssl
        )

        if r.status_code == 201:
            return r.json()
        else:
            status_code_error(r.status_code)


    def get_passwords_folder(self, name):
        for folder in self.list_passwords_folders():
            if folder.get('label') == name:
                return folder.get('id')
        return None


    def get_password(self, name):
        r = self.list_passwords()
        ret = []
        for item in r:
            if item['label'] == name:
                if self.details:
                    ret.append(item)
                else:
                    ret.append(item['password'])
        return ret

    def fetch_generated_password(self):
        r = self.get('index.php/apps/passwords/api/1.0/service/password')
        if r.status_code == 200:
            return [r.json().get('password')]
        else:
            status_code_error(r.status_code)


    def create_password(self, post_obj):
        r = requests.post(
            '{HTTP}://{HOST}/index.php/apps/passwords/api/1.0/password/create'.format(HTTP=self.HTTP, HOST=self.HOST), 
            data=post_obj, 
            headers=self.headers,
            auth=(self.USER, self.TOKEN),
            verify=self.ssl
        )

        if r.status_code == 201:
            return r.json()
        else:
            status_code_error(r.status_code)


    def delete_password(self, post_obj):
        r = requests.delete(
            '{HTTP}://{HOST}/index.php/apps/passwords/api/1.0/password/delete'.format(HTTP=self.HTTP, HOST=self.HOST), 
            data=post_obj, 
            headers=self.headers,
            auth=(self.USER, self.TOKEN),
            verify=self.ssl
        )

        if r.status_code == 200:
            return r.json()
        else:
            status_code_error(r.status_code)

    def update_password(self, post_obj):
        r = requests.patch(
            '{HTTP}://{HOST}/index.php/apps/passwords/api/1.0/password/update'.format(HTTP=self.HTTP, HOST=self.HOST), 
            data=post_obj, 
            headers=self.headers,
            auth=(self.USER, self.TOKEN),
            verify=self.ssl
        )

        if r.status_code == 200:
            return r.json()
        else:
            status_code_error(r.status_code)

    def user(self):
        return self.USER
