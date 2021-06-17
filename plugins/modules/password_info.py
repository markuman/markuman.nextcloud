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


def main():
    module = AnsibleModule(
        argument_spec = dict(
            host = dict(required=False, type='str'),
            api_token = dict(required=False, type='str', no_log=True, aliases=['access_token']),
            ssl_mode = dict(required=False, type='str', default='https'),
            name = dict(required=True, type='str')
        )
    )
    module.params["details"] = True
    nc = NextcloudHandler(module.params)

    retval = nc.list_passwords(module.params.get('name'))
    module.exit_json(**retval[0])
    

if __name__ == '__main__':
    main()