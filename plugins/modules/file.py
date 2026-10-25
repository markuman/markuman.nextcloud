#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: file
short_description: get/put/delete files from/to/on nextcloud
description:
  - Download files from Nextcloud.
  - Upload files to Nextcloud.
  - Delete files on Nextcloud.
version_added: "2.0.0"
author:
  - "Markus Bergholz (@markuman)"
options:
  mode:
    description:
      - Whether the file should be downloaded (V(get)), uploaded (V(put)) or deleted (V(delete)).
    required: true
    type: str
    choices: ['get', 'put', 'delete']
  source:
    description:
      - When the mode is V(get) or V(delete), source describes
        the file location on nextcloud.
      - When the mode is V(put), source describes the origin file
        location which will be uploaded to nextcloud.
    required: true
    aliases:
      - src
    type: str
  destination:
    description:
      - When the mode is V(get), destination will be
        the location of the downloaded file.
      - When the mode is V(put), destination describes
        the file location on nextcloud.
      - When the mode is V(delete), destination is not required.
    required: false
    aliases:
      - dest
    type: str
  overwrite:
    description:
      - Whether an existing destination is overwritten. Used with O(mode=get) and O(mode=put).
      - V(always) always transfers the file.
      - V(never) only transfers the file if the destination does not exist.
      - V(different) transfers the file if the sha256sum of source and destination differ.
        The remote file is downloaded (streamed) to calculate its checksum.
      - V(different_size) transfers the file if the size of source and destination differ.
    default: 'always'
    aliases: ['force', 'overwritten']
    choices: ['always', 'never', 'different', 'different_size']
    type: str
  delete_recursively:
    description:
      - Whether a target is deleted recursively.
      - Necessary for folders.
    required: false
    type: bool
    default: false
    version_added: 8.0.0
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode).
'''

EXAMPLES = '''
- name: fetch file from nextcloud
  markuman.nextcloud.file:
    mode: get
    source: anythingeverything.jpg
    destination: /tmp/anythingeverything.jpg
    host: nextcloud.tld
    user: myusername
    api_token: xxx

- name: upload file only if it differs
  markuman.nextcloud.file:
    mode: put
    src: /etc/hosts
    dest: backup/hosts
    overwrite: different

- name: delete a folder
  markuman.nextcloud.file:
    mode: delete
    src: old_stuff
    delete_recursively: true
'''

RETURN = '''
file:
  description: The requested transfer.
  returned: always
  type: dict
  sample: {"destination": "/tmp/test.jpg", "mode": "get", "source": "test.jpg"}
message:
  description: Human readable description of what happened.
  returned: always
  type: str
'''

import hashlib
import os
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_specs


def sha256sum(path):
    sha = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            sha.update(chunk)
    return sha.hexdigest()


def is_dir(facts):
    return facts.get('content_type') == 'inode/directory'


def mode_get(module, nc, source, destination, overwrite):
    if destination is None:
        module.fail_json(msg='No destination is given')

    remote = nc.dav_path(source)
    facts = nc.propfind(remote)
    if facts == {}:
        return False, "Requested file does not exist."
    if is_dir(facts):
        module.fail_json(msg='{0} is a folder, only files can be downloaded'.format(source))

    exists = os.path.isfile(destination)
    if exists and overwrite == 'never':
        return False, "Destination already exists."
    if exists and overwrite == 'different_size' and os.path.getsize(destination) == facts.get('size'):
        return False, "size of dest and src is equal."

    if exists and overwrite == 'different':
        local_sum = sha256sum(destination)
        if module.check_mode:
            if nc.download(remote, None) == local_sum:
                return False, "sha256sum of dest and src is equal."
            return True, "sha256sum of dest and src is not equal. But file was not written due check_mode."
    elif module.check_mode:
        return True, "File not received because of check_mode."

    dest_dir = os.path.dirname(os.path.abspath(destination))
    fd, tmp = tempfile.mkstemp(dir=dest_dir, prefix='.ansible_nextcloud_')
    try:
        with os.fdopen(fd, 'wb') as f:
            remote_sum = nc.download(remote, f)
        if exists and overwrite == 'different' and remote_sum == local_sum:
            os.remove(tmp)
            return False, "sha256sum of dest and src is equal."
        module.atomic_move(tmp, destination)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return True, "File received."


def mode_put(module, nc, source, destination, overwrite):
    if destination is None:
        module.fail_json(msg='No destination is given')
    if not os.path.isfile(source):
        module.fail_json(msg='Source file {0} does not exist'.format(source))

    remote = nc.dav_path(destination)
    facts = nc.propfind(remote)

    if facts != {}:
        if is_dir(facts):
            module.fail_json(msg='Destination {0} is a folder'.format(destination))
        if overwrite == 'never':
            return False, "Destination already exists."
        if overwrite == 'different_size' and os.path.getsize(source) == facts.get('size'):
            return False, "File not uploaded because size of dest and src is equal."
        if overwrite == 'different' and nc.download(remote, None) == sha256sum(source):
            return False, "File not uploaded because sha256sum of dest and src is equal."

    if module.check_mode:
        return True, "File not uploaded due check_mode."

    nc.put(remote, source)
    return True, "File uploaded."


def mode_delete(module, nc, source, delete_recursively):
    remote = nc.dav_path(source)
    facts = nc.propfind(remote)
    if facts == {}:
        return False, "File does not exist."

    if is_dir(facts) and not delete_recursively:
        return False, "Cannot delete folder without set delete_recursively to true."

    what = "Folder" if is_dir(facts) else "File"
    if module.check_mode:
        return True, "{0} not deleted due check_mode.".format(what)

    r, change = nc.delete(remote)
    return change, "{0} deleted.".format(what)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_specs(
            dict(
                mode=dict(required=True, type='str', choices=['get', 'put', 'delete']),
                source=dict(required=True, type='str', aliases=['src']),
                destination=dict(required=False, type='str', aliases=['dest']),
                overwrite=dict(required=False, type='str', default='always', aliases=['force', 'overwritten'],
                               choices=['always', 'never', 'different', 'different_size']),
                delete_recursively=dict(required=False, type='bool', default=False)
            )
        )
    )

    nc = NextcloudHandler(module.params, module.fail_json)

    mode = module.params.get("mode")
    source = module.params.get("source")
    destination = module.params.get("destination")
    overwrite = module.params.get("overwrite")

    if mode == "get":
        change, message = mode_get(module, nc, source, destination, overwrite)
    elif mode == "put":
        change, message = mode_put(module, nc, source, destination, overwrite)
    else:
        change, message = mode_delete(module, nc, source, module.params.get("delete_recursively"))

    module.exit_json(changed=change, file={'destination': destination, 'mode': mode, 'source': source}, message=message)


if __name__ == '__main__':
    main()
