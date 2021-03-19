#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
module: markuman.nextcloud.talk
short_description: send nextcloud talk messages
description:
  - send messages with nextcloud talk.
version_added: "3.0.0"
author:
  - "Markus Bergholz"
requirements:
  - requests python module
options:
  api_token:
    description:
      - Nextcloud App Password.
      - Can also be set as ENV variable.
    required: false
    type: str
  user:
    description:
      - Nextcloud user who (will) owns the file.
      - Can also be set as ENV variable.
    required: false
    type: str
  host:
    description:
      - Nextcloud tld host.
      - Can also be set as ENV variable.
    required: false
    type: str
  message:
    description:
      - Message that will be send.
    required: true
    type: str
  channel:
    description:
      - ID of the Nextcloud Talk channel.
    required: true
    type: str
  ssl_mode:
    description:
      - ability to use http:// for integration tests
      - ability to skip ssl verification
      - Possible values `https` (default https), `http` (http), `skip` (https) 
    required: false
    type: str
    default: https
    version_added: 3.0.3
'''

EXAMPLES = '''
    - name: send hello
      markuman.nextcloud.talk:
        message: Ho Hi!
        channel: someid
'''

from ansible.module_utils.basic import *
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
import json


def main():
    module = AnsibleModule(
        argument_spec = dict(
            message = dict(required=True, type='str'),
            channel = dict(required=True, type='str'),
            host = dict(required=False, type='str'),
            user = dict(required=False, type='str'),
            api_token = dict(required=False, type='str', no_log=True),
            ssl_mode = dict(required=False, type='str', default='https', choices=['https', 'http', 'skip'])
        )
    )

    nc = NextcloudHandler(module.params)

    message = module.params.get("message")
    channel = module.params.get("channel")

    headers = {
        'Accept': 'application/json',
        'OCS-APIRequest': 'true'
    }

    body = {
        'message': message,
        'replyTo': 0
    }

    r, change = nc.talk(message, channel)

    module.exit_json(changed = change, talk={'message': message, 'channel': channel})
    

if __name__ == '__main__':
    main()