# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import binascii
import hashlib
import json
import os
import traceback
from urllib.parse import quote
from xml.etree import ElementTree

from ansible.module_utils.common.parameters import env_fallback

REQUESTS_IMPORT_ERROR = None
try:
    import requests
    import urllib3
    HAS_REQUESTS_LIB = True
except ImportError:
    HAS_REQUESTS_LIB = False
    REQUESTS_IMPORT_ERROR = traceback.format_exc()

PYSODIUM_IMPORT_ERROR = None
try:
    import pysodium
    HAS_PYSODIUM_LIB = True
except ImportError:
    HAS_PYSODIUM_LIB = False
    PYSODIUM_IMPORT_ERROR = traceback.format_exc()

# kept for backwards compatibility
IMPORT_ERROR = REQUESTS_IMPORT_ERROR or PYSODIUM_IMPORT_ERROR

# (connect, read) timeout in seconds
TIMEOUT = (15, 300)

PASSWORDS_API = 'index.php/apps/passwords/api/1.0'
PASSWORDS_ROOT_FOLDER = '00000000-0000-0000-0000-000000000000'

DAV_NS = {
    'd': 'DAV:',
    'oc': 'http://owncloud.org/ns',
    'nc': 'http://nextcloud.org/ns',
}

PROPFIND_BODY = """<?xml version="1.0"?>
<d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">
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


class NextcloudError(Exception):
    pass


def parameter_specs(spec_arguments):
    argument_spec = dict(
        host=dict(type='str', fallback=(env_fallback, ['NEXTCLOUD_HOST'])),
        api_token=dict(type='str', no_log=True, aliases=['access_token'], fallback=(env_fallback, ['NEXTCLOUD_TOKEN'])),
        user=dict(type='str', fallback=(env_fallback, ['NEXTCLOUD_USER'])),
        ssl_mode=dict(type='str', default='https', choices=['https', 'http', 'skip'], fallback=(env_fallback, ['NEXTCLOUD_SSL_MODE'])),
    )
    argument_spec.update(spec_arguments)
    return argument_spec


# old (misspelled) name, still imported by third party code
parameter_spects = parameter_specs


def decrypt(encrypted, key):
    nonce = encrypted[0:pysodium.crypto_secretbox_NONCEBYTES]
    ciphertext = encrypted[pysodium.crypto_secretbox_NONCEBYTES:]
    return pysodium.crypto_secretbox_open(ciphertext, nonce, key)


def decrypt_item(item_key, item, key='label'):
    if not item.get(key):
        return ""
    vals = binascii.unhexlify(item[key])
    return decrypt(vals, binascii.unhexlify(item_key)).decode()


def _text(element):
    if element is None or element.text is None:
        return None
    return element.text


def _int(element):
    value = _text(element)
    return int(value) if value is not None else None


def parse_propfind(content):
    """ parse the multistatus answer of a depth 0 PROPFIND """
    root = ElementTree.fromstring(content)
    response = root.find('d:response', DAV_NS)
    if response is None:
        return {}

    prop = None
    for propstat in response.findall('d:propstat', DAV_NS):
        status = _text(propstat.find('d:status', DAV_NS)) or ''
        if ' 200 ' in status:
            prop = propstat.find('d:prop', DAV_NS)
            break
    if prop is None:
        return {}

    is_dir = prop.find('d:resourcetype/d:collection', DAV_NS) is not None

    return {
        'last_modified': _text(prop.find('d:getlastmodified', DAV_NS)),
        'etag': (_text(prop.find('d:getetag', DAV_NS)) or '').strip('"') or None,
        'content_type': 'inode/directory' if is_dir else _text(prop.find('d:getcontenttype', DAV_NS)),
        'file_id': _int(prop.find('oc:fileid', DAV_NS)),
        'size': _int(prop.find('oc:size', DAV_NS)),
        'favorite': _int(prop.find('oc:favorite', DAV_NS)),
        'owner': _text(prop.find('oc:owner-display-name', DAV_NS)),
        'href': _text(response.find('d:href', DAV_NS)),
    }


class NextcloudHandler:
    """
    Small client for the nextcloud APIs used by this collection.

    `fail_json` is called with a `msg` keyword on every error. Modules hand in
    `module.fail_json` (which never returns), plugins hand in a function that
    raises. If the callable returns anyway, a NextcloudError is raised.
    """

    def __init__(self, params, fail_json):
        self._fail_json = fail_json

        if not HAS_REQUESTS_LIB:
            self.fail('The python requests library is required: {0}'.format(REQUESTS_IMPORT_ERROR))

        # env fallback is still evaluated here for plugins that hand in raw params
        ssl_mode = params.get('ssl_mode') or os.environ.get('NEXTCLOUD_SSL_MODE') or 'https'
        if ssl_mode == 'https' and os.environ.get('NEXTCLOUD_SSL_MODE') in ('http', 'skip'):
            ssl_mode = os.environ.get('NEXTCLOUD_SSL_MODE')
        if ssl_mode not in ('https', 'http', 'skip'):
            self.fail('ssl_mode must be one of https, http or skip, got {0}'.format(ssl_mode))

        self.HTTP = 'http' if ssl_mode == 'http' else 'https'
        self.ssl = ssl_mode != 'skip'

        self.details = params.get('details') or False
        self.x_api_session = None

        self.HOST = params.get('host') or os.environ.get('NEXTCLOUD_HOST')
        if not self.HOST:
            self.fail('Unable to continue. No Nextcloud Host is given.')

        self.USER = params.get('user') or os.environ.get('NEXTCLOUD_USER')
        if not self.USER:
            self.fail('Unable to continue. No Nextcloud User is given.')

        self.TOKEN = params.get('api_token') or os.environ.get('NEXTCLOUD_TOKEN')
        if not self.TOKEN:
            self.fail('Unable to continue. No Nextcloud Token is given.')

        # host may be given as plain hostname (cloud.example.com),
        # with port (localhost:8443) or as full base url (https://example.com/nextcloud)
        host = self.HOST.rstrip('/')
        if '://' in host:
            self.base_url = host
        else:
            self.base_url = '{0}://{1}'.format(self.HTTP, host)

        self.session = requests.Session()
        self.session.auth = (self.USER, self.TOKEN)
        self.session.verify = self.ssl
        if not self.ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.E2E_PASSWORD = False
        password = params.get('cse_password') or os.environ.get('NEXTCLOUD_CSE_PASSWORD')
        if password:
            self._open_cse_session(password)

    # ------------------------------------------------------------------ helpers

    def fail(self, msg):
        self._fail_json(msg=msg)
        raise NextcloudError(msg)

    def status_code_error(self, status, msg=None):
        self.fail(msg or 'Nextcloud returned with status code {0}'.format(status))

    def user(self):
        return self.USER

    def url(self, path):
        return '{0}/{1}'.format(self.base_url, path.lstrip('/'))

    def dav_path(self, path):
        return 'remote.php/dav/files/{0}/{1}'.format(quote(self.USER), quote(path.lstrip('/')))

    def headers(self, extra=None):
        headers = {
            'Accept': 'application/json',
            'OCS-APIRequest': 'true'
        }
        if self.x_api_session:
            headers['X-API-SESSION'] = self.x_api_session
        if extra:
            headers.update(extra)
        return headers

    def request(self, method, path, expected=(200,), **kwargs):
        kwargs.setdefault('headers', self.headers())
        kwargs.setdefault('timeout', TIMEOUT)
        try:
            r = self.session.request(method, self.url(path), **kwargs)
        except requests.exceptions.RequestException as e:
            self.fail('Request {0} {1} failed: {2}'.format(method, self.url(path), e))

        if r.status_code not in expected:
            detail = ''
            try:
                body = r.json()
                detail = body.get('message') or body.get('error') or body.get('ocs', {}).get('meta', {}).get('message') or ''
            except Exception:
                pass
            msg = 'Nextcloud returned with status code {0} for {1} {2}'.format(r.status_code, method, path)
            if detail:
                msg = '{0}: {1}'.format(msg, detail)
            self.status_code_error(r.status_code, msg)
        return r

    # ------------------------------------------------------------------ generic

    def get(self, path, **kwargs):
        return self.request('GET', path, **kwargs)

    def ocs(self, method, path, **kwargs):
        """ request an OCS v2 endpoint and return the ocs.data part """
        r = self.request(method, path, **kwargs)
        if r.status_code == 404:
            return None
        return r.json().get('ocs', {}).get('data')

    def propfind(self, path):
        r = self.request(
            'PROPFIND', path,
            expected=(207, 404),
            headers={'Depth': '0', 'Content-Type': 'application/xml; charset=utf-8'},
            data=PROPFIND_BODY,
        )
        if r.status_code == 404:
            return {}
        return parse_propfind(r.content)

    def put(self, path, src=None):
        if src:
            with open(src, 'rb') as f:
                r = self.request('PUT', path, expected=(200, 201, 204, 404, 409), headers={}, data=f)
            # older versions answer with 409, newer with 404
            if r.status_code in (404, 409):
                self.fail('Unable to upload to {0}: parent folder does not exist'.format(path))
        else:
            r = self.request('PUT', path, expected=(200, 201, 204))
        return r, True

    def delete(self, path):
        r = self.request('DELETE', path, expected=(200, 204, 404), headers={})
        return r, r.status_code != 404

    def download(self, path, fileobj):
        """ stream a remote file into fileobj and return its sha256 hexdigest """
        sha = hashlib.sha256()
        with self.request('GET', path, headers={}, stream=True) as r:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                sha.update(chunk)
                if fileobj is not None:
                    fileobj.write(chunk)
        return sha.hexdigest()

    # ------------------------------------------------------------------ talk

    def talk(self, message, channel):
        body = {
            'message': message,
            'replyTo': 0
        }
        r = self.request('POST', 'ocs/v2.php/apps/spreed/api/v1/chat/{0}'.format(quote(channel)), expected=(201,), json=body)
        return r, True

    # ------------------------------------------------------------------ passwords

    def _open_cse_session(self, password):
        """ manage passwords client side encryption """
        if not HAS_PYSODIUM_LIB:
            self.fail('The python pysodium library is required for cse_password: {0}'.format(PYSODIUM_IMPORT_ERROR))

        self.E2E_PASSWORD = True
        retval = self.request_passwords_session()
        passwordSalt = binascii.unhexlify(retval['challenge']['salts'][0])
        genericHashKey = binascii.unhexlify(retval['challenge']['salts'][1])
        passwordHashSalt = binascii.unhexlify(retval['challenge']['salts'][2])

        genericHash = pysodium.crypto_generichash(
            password.encode() + passwordSalt,
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
        self.cse = self.open_passwords_session(passwordHash.hex())
        # decrypt CSEv1r1 chain
        vals = binascii.unhexlify(self.cse['keys']['CSEv1r1'])
        salt = vals[0:pysodium.crypto_pwhash_SALTBYTES]
        text = vals[pysodium.crypto_pwhash_SALTBYTES:]
        key = pysodium.crypto_pwhash(
            pysodium.crypto_box_SEEDBYTES,
            password.encode(),
            salt,
            pysodium.crypto_pwhash_OPSLIMIT_INTERACTIVE,
            pysodium.crypto_pwhash_MEMLIMIT_INTERACTIVE,
            pysodium.crypto_pwhash_ALG_ARGON2ID13
        )
        self.keychain = json.loads(decrypt(text, key))

    def passwords_api(self, method, action, expected=(200,), data=None):
        r = self.request(method, '{0}/{1}'.format(PASSWORDS_API, action), expected=expected, json=data)
        return r.json()

    def request_passwords_session(self):
        return self.passwords_api('GET', 'session/request')

    def open_passwords_session(self, passwordHash):
        r = self.request('POST', '{0}/session/open'.format(PASSWORDS_API), json={'challenge': passwordHash})
        self.x_api_session = r.headers.get('X-API-SESSION')
        return r.json()

    def close_passwords_session(self):
        return self.passwords_api('GET', 'session/close')

    def list_passwords(self):
        return self.passwords_api('GET', 'password/list')

    def list_passwords_folders(self):
        return self.passwords_api('GET', 'folder/list')

    def create_passwords_folder(self, name):
        return self.passwords_api('POST', 'folder/create', expected=(201,), data={'label': name})

    def get_passwords_folder(self, name):
        for folder in self.list_passwords_folders():
            if folder.get('label') == name:
                return folder.get('id')
        return None

    def get_password(self, name):
        ret = []
        for item in self.list_passwords():
            if item.get('cseType') == 'CSEv1r1' and self.E2E_PASSWORD:
                item_key = self.keychain['keys'].get(item['cseKey'])
                if item_key and decrypt_item(item_key, item, 'label') == name:
                    if self.details:
                        for field in ('password', 'url', 'username', 'label', 'notes', 'customFields'):
                            item[field] = decrypt_item(item_key, item, field)
                        ret.append(item)
                    else:
                        ret.append(decrypt_item(item_key, item, 'password'))
            elif item.get('label') == name:
                ret.append(item if self.details else item['password'])
        return ret

    def fetch_generated_password(self):
        return [self.passwords_api('GET', 'service/password').get('password')]

    def create_password(self, post_obj):
        return self.passwords_api('POST', 'password/create', expected=(201,), data=post_obj)

    def delete_password(self, post_obj):
        return self.passwords_api('DELETE', 'password/delete', data=post_obj)

    def update_password(self, post_obj):
        return self.passwords_api('PATCH', 'password/update', data=post_obj)


# kept for backwards compatibility
class NextcloudErrorHandler:
    def __init__(self, fail_json):
        self.fail = fail_json

    def status_code_error(self, status):
        self.fail(msg='Nextcloud returned with status code {SC}'.format(SC=status))
