#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: talk
short_description: send nextcloud talk messages
description:
  - send messages with nextcloud talk.
version_added: "3.0.0"
author:
  - "Markus Bergholz (@markuman)"
options:
  msg:
    description:
      - Message that will be send.
    required: true
    type: str
  channel:
    description:
      - ID of the Nextcloud Talk channel.
    required: true
    type: str
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode).
'''

EXAMPLES = '''
    - name: send hello
      markuman.nextcloud.talk:
        msg: Ho Hi!
        channel: someid
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_spects
import json


def main():
    module = AnsibleModule(
        argument_spec=parameter_spects(dict(
            msg=dict(required=True, type='str'),
            channel=dict(required=True, type='str')
        ))
    )

    nc = NextcloudHandler(module.params, module.fail_json)

    message = module.params.get("msg")
    channel = module.params.get("channel")

    headers = {
        'Accept': 'application/json',
        'OCS-APIRequest': 'true'
    }

    r, change = nc.talk(message, channel)

    module.exit_json(changed=change, talk={'message': message, 'channel': channel})


if __name__ == '__main__':
    main()
