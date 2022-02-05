#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: file_info
short_description: info about files in nextcloud
description:
  - collect informations about files and folders in nextcloud
version_added: "8.0.0"
author:
  - "Markus Bergholz (@markuman)"
options:
  source:
    description:
      - file or folder in nextcloud
    required: true
    aliases:
      - src
    type: str
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode).
'''

EXAMPLES = '''
    - name: fetch file from nextcloud
      markuman.nextcloud.file_info:
        source: anythingeverything.jpg
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_spects
import os.path
import hashlib


def write_file(destination, content):
    with open(destination, 'wb') as FILE:
        FILE.write(content)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_spects(dict(
            source=dict(required=True, type='str', aliases=['src'])
        ))
    )

    nc = NextcloudHandler(module.params, module.fail_json)

    source = module.params.get("source")

    change = False
    r = nc.propfind("remote.php/dav/files/{USER}/{SRC}".format(USER=nc.user(), SRC=source))

    if r != {}:
        r['source'] = source

    module.exit_json(changed=change, file_info=r)


if __name__ == '__main__':
    main()
