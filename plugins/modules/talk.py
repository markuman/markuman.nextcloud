#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
      - Token of the Nextcloud Talk conversation.
    required: true
    type: str
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode). In check mode no message is sent.
'''

EXAMPLES = '''
- name: send hello
  markuman.nextcloud.talk:
    msg: Ho Hi!
    channel: someid
'''

RETURN = '''
talk:
  description: The message and the channel.
  returned: always
  type: dict
  sample: {"message": "Ho Hi!", "channel": "someid"}
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_specs


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_specs(dict(
            msg=dict(required=True, type='str'),
            channel=dict(required=True, type='str')
        ))
    )

    nc = NextcloudHandler(module.params, module.fail_json)

    message = module.params.get("msg")
    channel = module.params.get("channel")

    if not module.check_mode:
        nc.talk(message, channel)

    module.exit_json(changed=True, talk={'message': message, 'channel': channel})


if __name__ == '__main__':
    main()
