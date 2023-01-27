#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: password_info
short_description: module to fetch password details
description:
  - Add, remove, enable or disable users
version_added: "7.0.0"
author:
  - "Markus Bergholz (@markuman)"
options:
  name:
    description:
      - Name represents the label of the password.
    required: false
    type: str
  cse_password:
    description:
      - Password for client side encryption.
    required: false
    type: str
    version_added: 9.3.0
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode).

'''

EXAMPLES = '''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_spects


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_spects(dict(
            name=dict(required=False, type='str'),
            cse_password=dict(required=False, type='str', no_log=True)
        ))
    )
    module.params["details"] = True
    nc = NextcloudHandler(module.params, module.fail_json)

    if module.params.get('name'):
        retval = nc.get_password(module.params.get('name'))
    else:
        retval = nc.list_passwords()

    module.exit_json(password=retval)


if __name__ == '__main__':
    main()
