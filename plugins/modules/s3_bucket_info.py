#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: s3_bucket_info
short_description: info about buckets and access keys of the nextcloud s3_api app
description:
  - List the buckets of O(user) in the L(S3 API app,https://apps.nextcloud.com/apps/s3_api)
    together with their access keys.
  - Secret keys are never returned, the s3_api app shows them only once when a key is created.
  - Fails if the s3_api app is not installed or not enabled for O(user).
version_added: "35.0.0"
author:
  - "Markus Bergholz (@markuman)"
options:
  name:
    description:
      - Name of a bucket.
      - When omitted, all buckets of O(user) are returned.
    type: str
    aliases: ['bucket']
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode).
  - Requires the s3_api app >= 1.7.0.
'''

EXAMPLES = '''
- name: list all buckets
  markuman.nextcloud.s3_bucket_info:
  register: out

- name: show the bucket names
  ansible.builtin.debug:
    msg: "{{ out.buckets | map(attribute='bucket_name') }}"

- name: access keys of the backup bucket
  markuman.nextcloud.s3_bucket_info:
    name: backup
  register: out
'''

RETURN = '''
buckets:
  description:
    - List of buckets, empty if O(name) does not exist.
    - Every bucket contains its C(access_keys) without the secret key.
  returned: always
  type: list
  elements: dict
  sample: [{"id": 3, "user_id": "alice", "bucket_name": "backup", "folder_path": "/S3/backup",
            "created_at": "2026-10-26T12:34:56+00:00",
            "access_keys": [{"id": 7, "bucket_id": 3, "access_key": "K3J9QZ8A1B2C3D4E5F6G", "permission": "readwrite",
                             "label": "restic", "created_at": "2026-10-26T12:34:56+00:00"}]}]
endpoint_url:
  description: S3 endpoint url of the Nextcloud instance.
  returned: always
  type: str
  sample: https://cloud.example.com/index.php/apps/s3_api/s3
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_specs
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import snake
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import S3_BUCKET_FIELDS
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import S3_KEY_FIELDS


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_specs(dict(
            name=dict(type='str', aliases=['bucket']),
        ))
    )
    nc = NextcloudHandler(module.params, module.fail_json)
    name = module.params.get('name')

    buckets = []
    for item in nc.s3_list_buckets():
        if name and item.get('bucketName') != name:
            continue
        bucket = snake(item, S3_BUCKET_FIELDS)
        bucket['access_keys'] = [snake(k, S3_KEY_FIELDS) for k in nc.s3_list_keys(item['id'])]
        buckets.append(bucket)

    module.exit_json(changed=False, buckets=buckets, endpoint_url=nc.s3_endpoint_url())


if __name__ == '__main__':
    main()
