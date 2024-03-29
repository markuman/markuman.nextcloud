from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
import traceback
from xml.dom import minidom
import binascii
import json

try:
    import requests
    HAS_REQUESTS_LIB = True
except ImportError:
    HAS_REQUESTS_LIB = False
    IMPORT_ERROR = traceback.format_exc()

try:
    import pysodium
    HAS_PYSODIUM_LIB = True
except ImportError:
    HAS_PYSODIUM_LIB = False
    IMPORT_ERROR = traceback.format_exc()


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


class NextcloudErrorHandler:
    def __init__(self, fail_json):
        self.fail = fail_json

    def status_code_error(self, status):
        try:
            self.fail(msg='Nextcloud returned with status code {SC}'.format(SC=status))
        except Exception:
            self.fail('Nextcloud returned with status code {SC}'.format(SC=status))


def parameter_spects(spec_arguments):
    argument_spec = dict(
        host=dict(required=False, type='str'),
        api_token=dict(required=False, type='str', no_log=True, aliases=['access_token']),
        user=dict(required=False, type='str'),
        ssl_mode=dict(required=False, type='str', default='https')
    )

    return {**argument_spec, **spec_arguments}


def decrypt(encrypted, key):
    nonce = encrypted[0:pysodium.crypto_secretbox_NONCEBYTES]
    ciphertext = encrypted[pysodium.crypto_secretbox_NONCEBYTES:]
    return pysodium.crypto_secretbox_open(ciphertext, nonce, key)


def decrypt_item(item_key, item, key='label'):
    if len(item[key]) == 0:
        return ""
    vals = binascii.unhexlify(item[key])
    return decrypt(vals, binascii.unhexlify(item_key)).decode()


class NextcloudHandler:
    def __init__(self, params, fail_json):
        self.exit = NextcloudErrorHandler(fail_json)
        self.HTTP = 'https'
        self.ssl = True
        if params.get('ssl_mode') == 'http':
            self.HTTP = 'http'
        elif params.get('ssl_mode') == 'skip':
            self.ssl = False
        elif os.environ.get('NEXTCLOUD_SSL_MODE') == 'http':
            self.HTTP = 'http'
        elif os.environ.get('NEXTCLOUD_SSL_MODE') == 'skip':
            self.ssl = False

        self.details = params.get('details') or False
        self.x_api_session = None

        self.HOST = params.get('host') or os.environ.get('NEXTCLOUD_HOST')
        if self.HOST is None:
            self.exit.status_code_error('Unable to continue. No Nextcloud Host is given.')

        self.USER = params.get('user') or os.environ.get('NEXTCLOUD_USER')
        if self.USER is None:
            self.exit.status_code_error('Unable to continue. No Nextcloud User is given.')

        self.TOKEN = params.get('api_token') or os.environ.get('NEXTCLOUD_TOKEN')
        if self.TOKEN is None:
            self.exit.status_code_error('Unable to continue. No Nextcloud Token is given.')

        self.E2E_PASSWORD = False
        if params.get('cse_password') or os.environ.get('NEXTCLOUD_CSE_PASSWORD'):
            """
                manage passwords client side encryption
            """
            self.E2E_PASSWORD = True
            password = params.get('cse_password') or os.environ.get('NEXTCLOUD_CSE_PASSWORD')
            retval = self.request_passwords_session()
            passwordSalt = binascii.unhexlify(retval['challenge']['salts'][0])
            genericHashKey = binascii.unhexlify(retval['challenge']['salts'][1])
            passwordHashSalt = binascii.unhexlify(retval['challenge']['salts'][2])

            input = password.encode() + passwordSalt
            genericHash = pysodium.crypto_generichash(
                input,
                k=genericHashKey,
                outlen=pysodium.crypto_generichash_BYTES_MAX
            )
            passwordHash = pysodium.crypto_pwhash(
                pysodium.crypto_box_SEEDBYTES,
                genericHash,
                passwordHashSalt,
                pysodium.crypto_pwhash_OPSLIMIT_INTERACTIVE,
                pysodium.crypto_pwhash_MEMLIMIT_INTERACTIVE,
                pysodium.crypto_pwhash_ALG_ARGON2ID13
            )
            # self.cse['keys']['CSEv1r1']
            self.cse = self.open_passwords_session(passwordHash.hex())
            # decrypt CSEv1r1 chain
            vals = binascii.unhexlify(self.cse['keys']['CSEv1r1'])
            salt = vals[0:pysodium.crypto_pwhash_SALTBYTES]
            text = vals[pysodium.crypto_pwhash_SALTBYTES:]
            key = pysodium.crypto_pwhash(
                pysodium.crypto_box_SEEDBYTES,
                password,
                salt,
                pysodium.crypto_pwhash_OPSLIMIT_INTERACTIVE,
                pysodium.crypto_pwhash_MEMLIMIT_INTERACTIVE,
                pysodium.crypto_pwhash_ALG_ARGON2ID13
            )
            self.keychain = json.loads(decrypt(text, key))

    def headers(self):
        headers = {
            'Accept': 'application/json',
            'OCS-APIRequest': 'true'
        }
        if self.x_api_session:
            headers['X-API-SESSION'] = self.x_api_session
        return headers

    def get(self, path):
        r = requests.get(
            '{HTTP}://{HOST}/{PATH}'.format(HTTP=self.HTTP, HOST=self.HOST, PATH=path),
            auth=(self.USER, self.TOKEN), verify=self.ssl, headers=self.headers()
        )

        if r.status_code == 200:
            return r
        elif r.status_code == 404:
            self.exit.status_code_error('File {FILE} does not exist'.format(FILE=path))
        else:
            self.exit.status_code_error(r.status_code)

    def propfind(self, path):
        s = requests.Session()
        s.auth = (self.USER, self.TOKEN)
        r = s.request(
            method='PROPFIND',
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
            except Exception:
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
            self.exit.status_code_error(r.status_code)

    def put(self, path, src=None):

        if src:
            r = requests.put(
                '{HTTP}://{HOST}/{PATH}'.format(HTTP=self.HTTP, HOST=self.HOST, PATH=path),
                data=open(src, 'rb'), auth=(self.USER, self.TOKEN), verify=self.ssl
            )
        else:
            r = requests.put(
                '{HTTP}://{HOST}/{PATH}'.format(HTTP=self.HTTP, HOST=self.HOST, PATH=path),
                headers=self.headers, auth=(self.USER, self.TOKEN), verify=self.ssl
            )

        if r.status_code in [200, 201, 204]:
            return r, True
        else:
            self.exit.status_code_error(r.status_code)

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
            self.exit.status_code_error(r.status_code)

    def talk(self, message, channel):
        body = {
            'message': message,
            'replyTo': 0
        }

        spreed_v1_path = "ocs/v2.php/apps/spreed/api/v1/chat"

        r = requests.post(
            '{HTTP}://{HOST}/{V1}/{CHANNEL}'.format(HTTP=self.HTTP, HOST=self.HOST, V1=spreed_v1_path, CHANNEL=channel),
            data=body,
            headers=self.headers(),
            auth=(self.USER, self.TOKEN),
            verify=self.ssl
        )

        if r.status_code == 201:
            return r, True
        else:
            self.exit.status_code_error(r.status_code)

    def request_passwords_session(self):
        r = self.get("index.php/apps/passwords/api/1.0/session/request")
        if r.status_code == 200:
            return r.json()
        else:
            self.exit.status_code_error(r.status_code)

    def open_passwords_session(self, passwordHash):
        post_obj = {
            'challenge': passwordHash
        }

        r = requests.post(
            '{HTTP}://{HOST}/index.php/apps/passwords/api/1.0/session/open'.format(HTTP=self.HTTP, HOST=self.HOST),
            data=post_obj,
            headers=self.headers(),
            auth=(self.USER, self.TOKEN),
            verify=self.ssl
        )
        if r.status_code == 200:
            self.x_api_session = r.headers.get('X-API-SESSION')
            return r.json()
        else:
            self.exit.status_code_error(r.status_code)

    def close_passwords_session(self):
        r = self.get("index.php/apps/passwords/api/1.0/session/close")
        if r.status_code == 200:
            return r.json()
        else:
            self.exit.status_code_error(r.status_code)

    def list_passwords(self):
        r = self.get("index.php/apps/passwords/api/1.0/password/list")
        if r.status_code == 200:
            return r.json()
        else:
            self.exit.status_code_error(r.status_code)

    def list_passwords_folders(self):
        r = self.get("index.php/apps/passwords/api/1.0/folder/list")
        if r.status_code == 200:
            return r.json()
        else:
            self.exit.status_code_error(r.status_code)

    def create_passwords_folder(self, name):
        post_obj = {
            'label': name
        }

        r = requests.post(
            '{HTTP}://{HOST}/index.php/apps/passwords/api/1.0/folder/create'.format(HTTP=self.HTTP, HOST=self.HOST),
            data=post_obj,
            headers=self.headers(),
            auth=(self.USER, self.TOKEN),
            verify=self.ssl
        )

        if r.status_code == 201:
            return r.json()
        else:
            self.exit.status_code_error(r.status_code)

    def get_passwords_folder(self, name):
        for folder in self.list_passwords_folders():
            if folder.get('label') == name:
                return folder.get('id')
        return None

    def get_password(self, name):
        r = self.list_passwords()
        ret = []
        for item in r:
            if item['cseType'] == 'CSEv1r1' and self.E2E_PASSWORD:
                item_key = self.keychain['keys'].get(item['cseKey'])
                if item_key:
                    if decrypt_item(item_key, item, 'label') == name:
                        if self.details:
                            item['password'] = decrypt_item(item_key, item, 'password')
                            item['url'] = decrypt_item(item_key, item, 'url')
                            item['username'] = decrypt_item(item_key, item, 'username')
                            item['label'] = decrypt_item(item_key, item, 'label')
                            item['notes'] = decrypt_item(item_key, item, 'notes')
                            item['customFields'] = decrypt_item(item_key, item, 'customFields')
                            ret.append(item)
                        else:
                            ret.append(decrypt_item(item_key, item, 'password'))
            else:
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
            self.exit.status_code_error(r.status_code)

    def create_password(self, post_obj):
        r = requests.post(
            '{HTTP}://{HOST}/index.php/apps/passwords/api/1.0/password/create'.format(HTTP=self.HTTP, HOST=self.HOST),
            data=post_obj,
            headers=self.headers(),
            auth=(self.USER, self.TOKEN),
            verify=self.ssl
        )

        if r.status_code == 201:
            return r.json()
        else:
            self.exit.status_code_error(r.status_code)

    def delete_password(self, post_obj):
        r = requests.delete(
            '{HTTP}://{HOST}/index.php/apps/passwords/api/1.0/password/delete'.format(HTTP=self.HTTP, HOST=self.HOST),
            data=post_obj,
            headers=self.headers(),
            auth=(self.USER, self.TOKEN),
            verify=self.ssl
        )

        if r.status_code == 200:
            return r.json()
        else:
            self.exit.status_code_error(r.status_code)

    def update_password(self, post_obj):
        r = requests.patch(
            '{HTTP}://{HOST}/index.php/apps/passwords/api/1.0/password/update'.format(HTTP=self.HTTP, HOST=self.HOST),
            data=post_obj,
            headers=self.headers(),
            auth=(self.USER, self.TOKEN),
            verify=self.ssl
        )

        if r.status_code == 200:
            return r.json()
        else:
            self.exit.status_code_error(r.status_code)

    def user(self):
        return self.USER
