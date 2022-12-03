#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: user
short_description: administrate nextcloud users
description:
  - disable or enable users
version_added: "9.3.0"
author:
  - "Markus Bergholz (@markuman)"
options:
  username:
    description:
      - Nextcloud username to receive detail information.
      - Nextcloud UserID
    required: true
    type: str
    aliases: ['user_id']
  enable:
    description:
      - Wether a user should be enabled or disabled.
    type: bool
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode).
'''

EXAMPLES = '''
- name: disable someuser
  markuman.nextcloud.user:
    username: someuser
    state: disable
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_spects
import copy
import traceback

try:
    import yaml
    HAS_YAML_LIB = True
except ImportError:
    HAS_YAML_LIB = False
    IMPORT_ERROR = traceback.format_exc()


def diff_handler(state_data, state):
    new_state = copy.deepcopy(state_data)
    new_state['enabled'] = state
    return new_state, dict(
        before=yaml.safe_dump(state_data),
        after=yaml.safe_dump(new_state)
    )


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_spects(dict(
            username=dict(required=True, type='str', aliases=['user_id']),
            enable=dict(type='bool')
        ))
    )

    nc = NextcloudHandler(module.params, module.fail_json)
    username = module.params.get('username')
    enable = module.params.get('enable')
    change = False

    retval = nc.get(f'/ocs/v1.php/cloud/users/{username}').json()
    current_state = retval.get('ocs', {}).get('data')

    if current_state and enable is not None:
        if enable is not current_state.get('enabled'):
            change = True
            state = 'disable'
            if enable:
                state = 'enable'

            if not module.check_mode:
                r, change = nc.put("ocs/v2.php/cloud/users/{USER}/{STATE}".format(USER=username, STATE=state))

        retval, diff = diff_handler(current_state, enable)
        module.exit_json(changed=change, diff=diff, user_data=retval)
    else:
        module.exit_json(changed=change, diff={'before': {}, 'after': {}}, user_data={})


if __name__ == '__main__':
    main()
