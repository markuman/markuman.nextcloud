# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = """
name: s3_buckets
author:
  - "Markus Bergholz (@markuman)"
version_added: 35.0.0
short_description: list the buckets of the nextcloud s3_api app
description:
  - Returns the names of all buckets of O(user) in the L(S3 API app,https://apps.nextcloud.com/apps/s3_api).
  - Fails if the s3_api app is not installed or not enabled for O(user).
  - Use C(query) or C(wantlist=true) to get a list, C(lookup) joins the names with commas.
options:
  details:
    description:
      - When V(false), only the bucket names are returned.
      - When V(true), the complete buckets (without access keys) are returned.
    type: bool
    default: false
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.plugin_connectivity
"""


EXAMPLES = """
- name: All bucket names
  ansible.builtin.debug:
    var: query('markuman.nextcloud.s3_buckets')

- name: All buckets with id, folder and creation date
  ansible.builtin.debug:
    var: query('markuman.nextcloud.s3_buckets', details=true, host='cloud.example.com', user='alice', api_token=app_password)
"""

RETURN = """
_raw:
  description:
    - List of bucket names.
    - With O(details=true) a list of dicts with C(id), C(user_id), C(bucket_name), C(folder_path) and C(created_at).
  type: list
"""

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import snake
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import S3_BUCKET_FIELDS


def _fail(msg):
    raise AnsibleLookupError(msg)


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        params = dict(
            (key, self.get_option(key))
            for key in ('host', 'user', 'api_token', 'ssl_mode')
        )

        nc = NextcloudHandler(params, _fail)
        buckets = nc.s3_list_buckets()
        if self.get_option('details'):
            return [snake(b, S3_BUCKET_FIELDS) for b in buckets]
        return [b['bucketName'] for b in buckets]
