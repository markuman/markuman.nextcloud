#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: user_info
short_description: administrate nextcloud users
description:
  - Add, remove, enable or disable users
version_added: "4.0.0"
author:
  - "Markus Bergholz (@markuman)"
options:
  username:
    version_added: "9.0.0"
    description:
      - Nextcloud username to receive detail information.
      - Nextcloud UserID
    required: false
    type: str
    aliases: ['user_id']
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode).
'''

EXAMPLES = '''
    - name: >
        user info
        returns list of all users
      markuman.nextcloud.user_info:
      register: out

    - name: >
        user info detailed
        returns details for one requested user
      markuman.nextcloud.user_info:
          username: some_user
      register: out
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_spects


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_spects(dict(
            username=dict(required=False, type='str', aliases=['user_id'])
        ))
    )

    nc = NextcloudHandler(module.params, module.fail_json)
    username = module.params.get('username')

    if username:
        retval = nc.get(f'/ocs/v1.php/cloud/users/{username}').json()
        module.exit_json(users=[username], user_data=retval.get('ocs', {}).get('data'))
    else:
        retval = nc.get('/ocs/v1.php/cloud/users').json()
        module.exit_json(users=retval.get('ocs', {}).get('data', {}).get('users', []), user_data={})


if __name__ == '__main__':
    main()
