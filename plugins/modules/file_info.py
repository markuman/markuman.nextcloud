#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
module: file_info
short_description: info about files in nextcloud
description:
  - collect information about files and folders in nextcloud
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
- name: fetch file information from nextcloud
  markuman.nextcloud.file_info:
    source: anythingeverything.jpg
  register: out
'''

RETURN = '''
file_info:
  description:
    - Properties of the file or folder.
    - Empty dict if it does not exist.
    - O(source), C(last_modified), C(etag), C(content_type) (V(inode/directory) for folders),
      C(file_id), C(size), C(favorite), C(owner), C(href).
  returned: always
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_specs


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_specs(dict(
            source=dict(required=True, type='str', aliases=['src'])
        ))
    )

    nc = NextcloudHandler(module.params, module.fail_json)
    source = module.params.get("source")

    r = nc.propfind(nc.dav_path(source))
    if r != {}:
        r['source'] = source

    module.exit_json(changed=False, file_info=r)


if __name__ == '__main__':
    main()
