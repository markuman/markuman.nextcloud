#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: markuman.nextcloud.user_info
short_description: administrate nextcloud users
description:
  - Add, remove, enable or disable users
version_added: "4.0.0"
author:
  - "Markus Bergholz"
requirements:
  - requests python module
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
