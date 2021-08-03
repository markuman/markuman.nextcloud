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
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode).
'''

EXAMPLES = '''
    - name: install and enable impersonate app
      markuman.nextcloud.user_info:
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_spects


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_spects({})
    )

    nc = NextcloudHandler(module.params)

    retval = nc.get('/ocs/v1.php/cloud/users').json()

    module.exit_json(users=retval.get('ocs', {}).get('data', {}).get('users', []))


if __name__ == '__main__':
    main()
