#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
module: user
short_description: administrate nextcloud users
description:
  - disable or enable users
  - Requires admin (or subadmin) privileges.
version_added: "9.3.0"
author:
  - "Markus Bergholz (@markuman)"
options:
  username:
    description:
      - Nextcloud username (Nextcloud UserID).
    required: true
    type: str
    aliases: ['user_id']
  enable:
    description:
      - Whether a user should be enabled or disabled.
      - When omitted, nothing is changed and only the user data is returned.
    type: bool
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode) and C(diff).
'''

EXAMPLES = '''
- name: disable someuser
  markuman.nextcloud.user:
    username: someuser
    enable: false
'''

RETURN = '''
user_data:
  description: Details of the user (after the change).
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
            username=dict(required=True, type='str', aliases=['user_id']),
            enable=dict(type='bool')
        ))
    )

    nc = NextcloudHandler(module.params, module.fail_json)
    username = module.params.get('username')
    enable = module.params.get('enable')
    path = 'ocs/v2.php/cloud/users/{0}'.format(quote(username, safe=''))

    user_data = nc.ocs('GET', path, expected=(200, 404))
    if not user_data:
        module.fail_json(msg='User {0} does not exist'.format(username))

    change = enable is not None and enable != user_data.get('enabled')
    diff = dict(before={'enabled': user_data.get('enabled')}, after={'enabled': user_data.get('enabled')})

    if change:
        diff['after']['enabled'] = enable
        if not module.check_mode:
            nc.request('PUT', '{0}/{1}'.format(path, 'enable' if enable else 'disable'))
            user_data = nc.ocs('GET', path)
        else:
            user_data['enabled'] = enable

    module.exit_json(changed=change, diff=diff, user_data=user_data)


if __name__ == '__main__':
    main()
