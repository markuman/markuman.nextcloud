#!/usr/bin/python
# -*- coding: utf-8 -*-

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

from ansible.module_utils.basic import *
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_spects


def main():
    module = AnsibleModule(
        argument_spec = parameter_spects(dict(
            name = dict(required=False, type='str')
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