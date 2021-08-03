#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: info
short_description: receive informations about nextcloud server
description:
  - receive informations about nextcloud server
version_added: "9.0.0"
author:
  - "Markus Bergholz (@markuman)"
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.connectivity
notes:
  - Supports C(check_mode).
'''

EXAMPLES = '''
    - name: receive informations
      markuman.nextcloud.info:
      register: out
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_spects


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=parameter_spects(dict())
    )

    nc = NextcloudHandler(module.params)

    retval = nc.get('/ocs/v1.php/cloud/capabilities').json()
    module.exit_json(nextcloud=retval.get('ocs').get('data'))


if __name__ == '__main__':
    main()
