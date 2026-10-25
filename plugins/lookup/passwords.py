# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = """
name: passwords
author:
  - "Markus Bergholz (@markuman)"
version_added: 0.0.1
short_description: read passwords from nextcloud "passwords" app
description:
  - This lookup returns the password stored in nextcloud passwords app based by label
  - See U(https://apps.nextcloud.com/apps/passwords)
options:
  _terms:
    description: Label(s) of the requested password(s).
    required: true
  details:
    description:
      - When V(false), only the password itself is returned.
      - When V(true), the complete password object is returned.
    type: bool
    default: false
  cse_password:
    description:
      - Password for client side encryption.
      - Requires the python library C(pysodium).
    type: str
    version_added: 11.0.0
    env:
      - name: NEXTCLOUD_CSE_PASSWORD
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.plugin_connectivity
"""


EXAMPLES = """
- name: Retrieve Password with label "Stackoverflow"
  ansible.builtin.debug:
    var: lookup('markuman.nextcloud.passwords', 'Stackoverflow', host='nextcloud.tld', user='ansible', api_token='some-token')

- name: Retrieve Password with all details, connection settings taken from NEXTCLOUD_* env vars
  ansible.builtin.debug:
    var: lookup('markuman.nextcloud.passwords', 'Stackoverflow', details=true)
"""

RETURN = """
_raw:
  description:
    - List of matching passwords.
    - With O(details=true) a list of dicts.
  type: list
"""

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler


def _fail(msg):
    raise AnsibleLookupError(msg)


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        params = dict(
            (key, self.get_option(key))
            for key in ('host', 'user', 'api_token', 'ssl_mode', 'details', 'cse_password')
        )

        nc = NextcloudHandler(params, _fail)
        ret = []
        for term in terms:
            ret.extend(nc.get_password(term))
        return ret
