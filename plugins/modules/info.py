#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
module: info
short_description: receive information about nextcloud server
description:
  - receive information (version and capabilities) about nextcloud server
version_added: "9.0.0"
author:
  - "Markus Bergholz (@markuman)"
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode).
'''

EXAMPLES = '''
- name: receive information
  markuman.nextcloud.info:
  register: out
'''

RETURN = '''
nextcloud:
  description: Version and capabilities of the nextcloud server.
  returned: always
  type: dict
  sample: {"version": {"major": 35, "minor": 0, "micro": 1, "string": "35.0.1"}, "capabilities": {}}
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_specs


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_specs(dict())
    )

    nc = NextcloudHandler(module.params, module.fail_json)

    module.exit_json(changed=False, nextcloud=nc.ocs('GET', 'ocs/v2.php/cloud/capabilities'))


if __name__ == '__main__':
    main()
