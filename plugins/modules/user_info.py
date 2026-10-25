#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
module: user_info
short_description: receive information about nextcloud users
description:
  - List all users or receive details of a single user.
  - Requires admin (or subadmin) privileges.
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

RETURN = '''
users:
  description:
    - List of all user ids.
    - When O(username) is given, a list with just this user, or an empty list if the user does not exist.
  returned: always
  type: list
  elements: str
user_data:
  description: Details of O(username). Empty dict if no O(username) is given or the user does not exist.
  returned: always
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_specs
from urllib.parse import quote


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_specs(dict(
            username=dict(required=False, type='str', aliases=['user_id'])
        ))
    )

    nc = NextcloudHandler(module.params, module.fail_json)
    username = module.params.get('username')

    if username:
        data = nc.ocs('GET', 'ocs/v2.php/cloud/users/{0}'.format(quote(username, safe='')), expected=(200, 404))
        if not data:
            module.exit_json(changed=False, users=[], user_data={})
        module.exit_json(changed=False, users=[username], user_data=data)
    else:
        data = nc.ocs('GET', 'ocs/v2.php/cloud/users') or {}
        module.exit_json(changed=False, users=data.get('users', []), user_data={})


if __name__ == '__main__':
    main()
