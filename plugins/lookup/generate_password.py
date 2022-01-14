from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase

from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
lookup: markuman.nextcloud.generate_password
author:
    - Markus Bergholz <markuman@gmail.com>
version_added: 7.0.0
short_description: fetch generated password from nextcloud password app
description:
    - fetch generated password from nextcloud password app
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
"""


EXAMPLES = """
- name: Retrieve Password with label "Stackoverflow"
  debug:
    var: lookup('markuman.nextcloud.generate_password', 'dokuwiki')
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
        return nc.fetch_generated_password()
