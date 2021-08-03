from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase

from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler

try:
    import requests
except ImportError:
    raise AnsibleError("Please install requests library.")

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

        nc = NextcloudHandler(kwargs)
        return nc.fetch_generated_password()
