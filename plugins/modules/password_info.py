#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: markuman.nextcloud.password_info
short_description: module to fetch password details
description:
  - Add, remove, enable or disable users
version_added: "7.0.0"
author:
  - "Markus Bergholz"
requirements:
  - requests python module
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
            name=dict(required=False, type='str')
        ))
    )
    module.params["details"] = True
    nc = NextcloudHandler(module.params)

    if module.params.get('name'):
        retval = nc.get_password(module.params.get('name'))
    else:
        retval = nc.list_passwords()

    module.exit_json(password=retval)


if __name__ == '__main__':
    main()
