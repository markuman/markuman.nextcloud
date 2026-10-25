#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
module: password_info
short_description: module to fetch password details
description:
  - Fetch passwords and their details from the nextcloud passwords app.
  - See U(https://apps.nextcloud.com/apps/passwords).
version_added: "7.0.0"
author:
  - "Markus Bergholz (@markuman)"
options:
  name:
    description:
      - Name represents the label of the password.
      - When omitted, all passwords are returned.
    required: false
    type: str
  cse_password:
    description:
      - Password for client side encryption.
      - Requires the python library C(pysodium).
      - Can also be set with the E(NEXTCLOUD_CSE_PASSWORD) environment variable.
    required: false
    type: str
    version_added: 11.0.0
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode).
'''

EXAMPLES = '''
- name: fetch a password
  markuman.nextcloud.password_info:
    name: my-database
  register: out

- name: show the password
  ansible.builtin.debug:
    msg: "{{ out.password[0].password }}"
'''

RETURN = '''
password:
  description: List of matching passwords with all details.
  returned: always
  type: list
  elements: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_specs


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_specs(dict(
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

    module.exit_json(changed=False, password=retval)


if __name__ == '__main__':
    main()
