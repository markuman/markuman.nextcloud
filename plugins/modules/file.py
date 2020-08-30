#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
module: markuman.nextcloud.file
short_description: get/put/delete files from/to/on nextcloud
description:
  - Download files from Nextcloud.
  - Upload files to Nextcloud.
  - Delete files on Nextcloud.
version_added: "2.0.0"
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
  mode:
    description:
      - Weather the file should be downloaded (get), uploaded (put) or deleted (delete).
    required: true
    type: str
  source:
    description:
      - When the mode is get or delete, source describes the file location on nextcloud.
      - When the mode is put, source describes the origin file location which will be uploaded to nextcloud.
    required: true
    aliases:
      - src
    type: str
  destination:
    description:
      - When the mode is get, destination will the location of the downloaded file.
      - When the mode is put, destination describes the file location on nextcloud.
      - When the mode is delete, destination is not required.
    required: false
    aliases:
      - dest
    type: str
'''

EXAMPLES = '''
    - name: fetch file from nextcloud
      markuman.nextcloud.file:
        mode: get
        source: anythingeverything.jpg
        destination: /tmp/anythingeverything.jpg
        host: nextcloud.tld
        user: myusername
        api_token: xxx
'''

from ansible.module_utils.basic import *
from ansible_collections.markuman.nextcloud.plugins.module_utils.auth import NextcloudHandler

def main():
    module = AnsibleModule(
        argument_spec = dict(
            mode = dict(required=True, type='str'),
            source = dict(required=True, type='str', aliases=['src']),
            destination = dict(required=False, type='str', aliases=['dest']),
            host = dict(required=False, type='str'),
            user = dict(required=False, type='str'),
            api_token = dict(required=False, type='str')
        )
    )

    nc = NextcloudHandler(module.params)

    mode = module.params.get("mode")
    source = module.params.get("source")
    destination = module.params.get("destination")

    if mode == "get":
        r = nc.get("remote.php/dav/files/{USER}/{SRC}".format(USER=nc.user(), SRC=source))
        with open(destination,'wb') as FILE:
            FILE.write(r.content)
        change = True


    module.exit_json(changed = change, file={'destination': destination, 'mode': mode, 'source': source})
    

if __name__ == '__main__':
    main()