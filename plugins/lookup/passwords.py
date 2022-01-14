from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler

try:
    import requests
    HAS_REQUESTS_LIB = True
except ImportError:
    HAS_REQUESTS_LIB = False

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
lookup: markuman.nextcloud.passwords
author:
    - Markus Bergholz <markuman@gmail.com>
version_added: 0.0.1
short_description: read passwords from nextcloud "passwords" app
description:
    - This lookup returns the password stored in nextcloud passwords app based by label
    - See U(https://apps.nextcloud.com/apps/passwords)
options:
  _terms:
    description: Label of the requested password.
    required: True
  host:
    description: host of the requested nextcloud instance (required https)
    required: True
  user:
    description: username of the requested nextcloud passwords user
    required: True
  api_token:
    description: generated api token of the user on the requested nextcloud passwords user
    required: True

notes:
    - This lookup plugin requires a https connection to the requested nextcloud instance.
"""


EXAMPLES = """
- name: Retrieve Password with label "Stackoverflow"
  debug:
    var: lookup('nextcloud_passwords', 'Stackoverflow' , host='nextcloud.tld', user='ansible', api_token='some-token', details=False)
"""


class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):
        params = dict()
        if kwargs.get('host'):
            params['host'] = kwargs.get('host')
        if kwargs.get('api_token'):
            params['api_token'] = kwargs.get('api_token')
        if kwargs.get('user'):
            params['user'] = kwargs.get('user')
        if kwargs.get('details') is not None:
            params['details'] = kwargs.get('details')
        if kwargs.get('ssl_mode') is not None:
            params['ssl_mode'] = kwargs.get('ssl_mode')

        nc = NextcloudHandler(params, AnsibleError)
        for term in terms:
            return nc.get_password(term)
