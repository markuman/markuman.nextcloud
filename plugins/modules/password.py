#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
module: markuman.nextcloud.password
short_description: module to manage passwords
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
from ansible.errors import AnsibleError


def main():
    module = AnsibleModule(
        argument_spec = dict(
            host = dict(required=False, type='str'),
            api_token = dict(required=False, type='str', no_log=True, aliases=['access_token']),
            user = dict(required=False, type='str'),
            ssl_mode = dict(required=False, type='str', default='https'),
            name = dict(required=True, type='str'),
            state = dict(type='str', choices=['present', 'absent'], default='present'),
            password = dict(required=False, type='str', no_log=True),
            update_password = dict(type='str', choices=['always', 'on_create'], default='on_create'),
            username = dict(required=False, type='str'),
            url = dict(required=False, type='str'),
            notes = dict(required=False, type='str'),
            favorite = dict(required=False, type='bool', default=False),
            folder = dict(required=False, type='str')
        ),
        supports_check_mode=True
    )
    module.params["details"] = True
    nc = NextcloudHandler(module.params)

    name = module.params.get('name')
    password = module.params.get('password') or nc.fetch_generated_password()
    username = module.params.get('username')
    url = module.params.get('url')
    notes = module.params.get('notes')
    state = module.params.get('state')
    favorite = module.params.get('favorite')
    update_password = module.params.get('update_password')
    folder = module.params.get('folder')


    retval = nc.get_password(name)

    if state == 'present':
        if len(retval) == 1:
            # update password
            if password == retval[0].get('password'):
                    module.exit_json(changed = False, password=retval)

            elif update_password == 'always' and password != retval[0].get('password'):
                obj = {
                    'id': retval[0].get('id'),
                    'password': password,
                    'label': name
                }

                if notes:
                    obj['notes'] = notes

                if username:
                    obj['username'] = username

                if url:
                    obj['url'] = url

                if favorite:
                    obj['favorite'] = favorite

                if not module.check_mode:
                    retval = nc.update_password(obj)

                module.exit_json(changed = True, password=retval)

            else:
                module.exit_json(changed = False, password=retval)

        elif len(retval) == 0:
            # create password
            obj = {
                'password': password,
                'label': name
            }

            if folder:
                if nc.get_passwords_folder(folder):
                    obj['folder'] = nc.get_passwords_folder(folder)
                else:
                    obj['folder'] = nc.create_passwords_folder(folder).get('id')

            if notes:
                obj['notes'] = notes

            if username:
                obj['username'] = username

            if url:
                obj['url'] = url

            if favorite:
                obj['favorite'] = favorite

            retval = {}
            if not module.check_mode:
                retval = nc.create_password(obj)

            module.exit_json(changed = True, password=retval)


        else:
            raise AnsibleError('More than one password identifies. Cannot continue')

    elif state == 'absent':
        if len(retval) == 1:
            if not module.check_mode:
                obj = {
                'id': retval[0].get('id')
              }
                retval = nc.delete_password(obj)
                module.exit_json(changed = True, password=retval)
            module.exit_json(changed = True, password={})
        elif len(retval) == 0:
            module.exit_json(changed = False, password={})
        else:
            raise AnsibleError('More than one password identifies. Cannot continue')

      

if __name__ == '__main__':
    main()