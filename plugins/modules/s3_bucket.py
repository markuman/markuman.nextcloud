#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: s3_bucket
short_description: manage buckets and access keys of the nextcloud s3_api app
description:
  - Create and delete buckets of the L(S3 API app,https://apps.nextcloud.com/apps/s3_api)
    and the access keys of a bucket.
  - A bucket is bound to a folder of O(user). Buckets and keys always belong to O(user),
    an admin cannot manage the buckets of other users with this module.
  - Fails if the s3_api app is not installed or not enabled for O(user).
version_added: "35.0.0"
author:
  - "Markus Bergholz (@markuman)"
options:
  name:
    description:
      - Name of the bucket.
      - Bucket names are unique per user. 3 to 63 characters, lowercase alphanumeric, dots and hyphens.
    required: true
    type: str
    aliases: ['bucket']
  state:
    description:
      - When V(present), the bucket and the keys in O(access_keys) are created.
      - When V(absent), the bucket is deleted together with all its keys.
        The folder and its files are kept.
    type: str
    choices: ['present', 'absent']
    default: present
  folder:
    description:
      - Folder of O(user) the bucket is bound to, for example V(/S3/backup).
      - Required to create a bucket.
      - The s3_api app has no API to move a bucket. If the bucket already exists with
        another folder, the module fails. Delete the bucket first.
      - The folder of a bucket must not overlap with the folder of another bucket of the same user.
    type: str
  create_folder:
    description:
      - Create O(folder) (and its parents) with WebDAV if it does not exist.
      - When V(false), a missing folder lets the bucket creation fail.
    type: bool
    default: false
  access_keys:
    description:
      - Access keys of the bucket. Keys are identified by their O(access_keys[].label).
      - The secret key is only returned once, when the key is created.
      - Keys that are not listed are kept, unless O(purge_keys=true).
    type: list
    elements: dict
    default: []
    aliases: ['keys']
    suboptions:
      label:
        description:
          - Label of the key. Must be unique within the bucket.
        type: str
        required: true
      permission:
        description:
          - Permission of the key.
          - The s3_api app cannot change the permission of a key. If an existing key has
            another permission, the key is deleted and recreated. This results in a new
            access key and secret key.
        type: str
        choices: ['readonly', 'readwrite']
        default: readonly
      state:
        description:
          - Whether the key should exist or not.
        type: str
        choices: ['present', 'absent']
        default: present
  purge_keys:
    description:
      - Delete all keys of the bucket whose label is not listed in O(access_keys).
        This includes keys without a label.
    type: bool
    default: false
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode).
  - Requires the s3_api app >= 1.7.0.
  - The secret keys of newly created keys are part of the module result.
    Use C(no_log) on the task and store them right away, for example with the M(markuman.nextcloud.password) module.
'''

EXAMPLES = '''
- name: create a bucket with a key for the backup client
  markuman.nextcloud.s3_bucket:
    name: backup
    folder: /S3/backup
    create_folder: true
    access_keys:
      - label: restic
        permission: readwrite
  register: bucket
  no_log: true

- name: store the secret in the passwords app
  markuman.nextcloud.password:
    name: s3-backup-restic
    username: "{{ item.access_key }}"
    password: "{{ item.secret_key }}"
    url: "{{ bucket.endpoint_url }}"
  loop: "{{ bucket.created_keys }}"
  no_log: true

- name: remove a single key and all unknown keys
  markuman.nextcloud.s3_bucket:
    name: backup
    purge_keys: true
    access_keys:
      - label: restic
        permission: readwrite
      - label: old-laptop
        state: absent

- name: delete the bucket and its keys, the folder is kept
  markuman.nextcloud.s3_bucket:
    name: backup
    state: absent
'''

RETURN = '''
bucket:
  description: The bucket. Empty when it does not exist (anymore) or in check mode before it is created.
  returned: always
  type: dict
  sample: {"id": 3, "user_id": "alice", "bucket_name": "backup", "folder_path": "/S3/backup", "created_at": "2026-10-26T12:34:56+00:00"}
access_keys:
  description:
    - All keys of the bucket after the changes.
    - Only newly created keys contain the C(secret_key).
  returned: always
  type: list
  elements: dict
  sample: [{"id": 7, "bucket_id": 3, "access_key": "K3J9QZ8A1B2C3D4E5F6G", "permission": "readwrite", "label": "restic",
            "created_at": "2026-10-26T12:34:56+00:00", "secret_key": "c2VjcmV0..."}]
created_keys:
  description: The keys created by this run, including their C(secret_key).
  returned: always
  type: list
  elements: dict
deleted_keys:
  description: The keys deleted by this run.
  returned: always
  type: list
  elements: dict
endpoint_url:
  description: S3 endpoint url of the Nextcloud instance.
  returned: always
  type: str
  sample: https://cloud.example.com/index.php/apps/s3_api/s3
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_specs

API = 'index.php/apps/s3_api/api/v1/buckets'

BUCKET_FIELDS = {
    'id': 'id',
    'userId': 'user_id',
    'bucketName': 'bucket_name',
    'folderPath': 'folder_path',
    'createdAt': 'created_at',
}

KEY_FIELDS = {
    'id': 'id',
    'bucketId': 'bucket_id',
    'accessKey': 'access_key',
    'permission': 'permission',
    'label': 'label',
    'createdAt': 'created_at',
    'secretKey': 'secret_key',
}


def snake(obj, fields):
    return dict((new, obj[old]) for old, new in fields.items() if old in obj)


def normalize(path):
    return '/' + path.strip('/')


class S3Api:

    def __init__(self, module, nc):
        self.module = module
        self.nc = nc

    def list_buckets(self):
        # a disabled app answers with 404 or redirects to the default app
        r = self.nc.request('GET', API, expected=(200, 302, 303, 404), allow_redirects=False)
        try:
            buckets = r.json()
        except ValueError:
            buckets = None
        if r.status_code != 200 or not isinstance(buckets, list):
            self.module.fail_json(msg='The s3_api app is not installed or not enabled for user {0} '
                                      '(GET {1} returned {2})'.format(self.nc.USER, API, r.status_code))
        return buckets

    def create_bucket(self, name, folder):
        return self.nc.request('POST', API, expected=(201,), json={'bucketName': name, 'folderPath': folder}).json()

    def delete_bucket(self, bucket_id):
        self.nc.request('DELETE', '{0}/{1}'.format(API, bucket_id))

    def list_keys(self, bucket_id):
        return self.nc.request('GET', '{0}/{1}/keys'.format(API, bucket_id)).json()

    def create_key(self, bucket_id, label, permission):
        return self.nc.request('POST', '{0}/{1}/keys'.format(API, bucket_id), expected=(201,),
                               json={'label': label, 'permission': permission}).json()

    def delete_key(self, bucket_id, key_id):
        self.nc.request('DELETE', '{0}/{1}/keys/{2}'.format(API, bucket_id, key_id))


def ensure_folder(module, nc, folder):
    """ create folder and its parents with MKCOL """
    current = ''
    for segment in folder.strip('/').split('/'):
        current = '{0}/{1}'.format(current, segment)
        facts = nc.propfind(nc.dav_path(current))
        if facts:
            if facts.get('content_type') != 'inode/directory':
                module.fail_json(msg='{0} exists but is not a folder'.format(current))
            continue
        if not module.check_mode:
            nc.request('MKCOL', nc.dav_path(current), expected=(201,), headers={})


def plan_keys(module, existing, wanted, purge):
    """ returns (to_create, to_delete) as lists of dicts """
    by_label = {}
    for key in existing:
        by_label.setdefault(key.get('label'), []).append(key)

    to_create = []
    to_delete = []
    for want in wanted:
        current = by_label.get(want['label'], [])
        if want['state'] == 'absent':
            to_delete.extend(current)
            continue
        if len(current) > 1:
            module.fail_json(msg='More than one key with label {0} exists. Cannot continue'.format(want['label']))
        if current and current[0].get('permission') == want['permission']:
            continue
        to_delete.extend(current)
        to_create.append(want)

    if purge:
        labels = set(want['label'] for want in wanted if want['state'] == 'present')
        for key in existing:
            if key.get('label') not in labels and key not in to_delete:
                to_delete.append(key)

    return to_create, to_delete


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_specs(dict(
            name=dict(required=True, type='str', aliases=['bucket']),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            folder=dict(type='str'),
            create_folder=dict(type='bool', default=False),
            access_keys=dict(type='list', elements='dict', default=[], no_log=False, aliases=['keys'], options=dict(
                label=dict(type='str', required=True),
                permission=dict(type='str', choices=['readonly', 'readwrite'], default='readonly'),
                state=dict(type='str', choices=['present', 'absent'], default='present'),
            )),
            purge_keys=dict(type='bool', default=False),
        ))
    )

    nc = NextcloudHandler(module.params, module.fail_json)
    api = S3Api(module, nc)

    name = module.params.get('name')
    state = module.params.get('state')
    folder = module.params.get('folder')

    result = dict(
        changed=False,
        bucket={},
        access_keys=[],
        created_keys=[],
        deleted_keys=[],
        endpoint_url=nc.url('index.php/apps/s3_api/s3'),
    )

    bucket = None
    for item in api.list_buckets():
        if item.get('bucketName') == name:
            bucket = item
            break

    if state == 'absent':
        if bucket:
            result['changed'] = True
            result['deleted_keys'] = [snake(k, KEY_FIELDS) for k in api.list_keys(bucket['id'])]
            if not module.check_mode:
                api.delete_bucket(bucket['id'])
        module.exit_json(**result)

    if bucket is None:
        if not folder:
            module.fail_json(msg='Bucket {0} does not exist and no folder is given to create it'.format(name))
        if module.params.get('create_folder'):
            ensure_folder(module, nc, folder)
        result['changed'] = True
        if not module.check_mode:
            bucket = api.create_bucket(name, normalize(folder))
    elif folder and normalize(folder) != normalize(bucket.get('folderPath') or '/'):
        module.fail_json(msg='Bucket {0} is bound to folder {1}, not {2}. Buckets cannot be moved, '
                             'delete the bucket first'.format(name, bucket.get('folderPath'), normalize(folder)))

    existing = api.list_keys(bucket['id']) if bucket else []
    to_create, to_delete = plan_keys(module, existing, module.params.get('access_keys'), module.params.get('purge_keys'))

    if to_create or to_delete:
        result['changed'] = True
    result['deleted_keys'] = [snake(k, KEY_FIELDS) for k in to_delete]

    if module.check_mode:
        result['bucket'] = snake(bucket, BUCKET_FIELDS) if bucket else {}
        result['created_keys'] = [dict(label=k['label'], permission=k['permission']) for k in to_create]
        result['access_keys'] = [snake(k, KEY_FIELDS) for k in existing if k not in to_delete] + result['created_keys']
        module.exit_json(**result)

    for key in to_delete:
        api.delete_key(bucket['id'], key['id'])
    created = [api.create_key(bucket['id'], k['label'], k['permission']) for k in to_create]

    deleted_ids = set(k['id'] for k in to_delete)
    keys = [k for k in existing if k['id'] not in deleted_ids] + created

    result['bucket'] = snake(bucket, BUCKET_FIELDS)
    result['access_keys'] = [snake(k, KEY_FIELDS) for k in keys]
    result['created_keys'] = [snake(k, KEY_FIELDS) for k in created]
    module.exit_json(**result)


if __name__ == '__main__':
    main()
