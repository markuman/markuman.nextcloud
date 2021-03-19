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
    aliases: ['access_token']
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
  overwrite:
    description:
      - Force overwrite locally on the filesystem
      - Used only with GET parameter.
      - one of [always, never, different]. different depends on md5sum.
    default: 'always'
    aliases: ['force']
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
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
import os.path
import hashlib

def write_file(destination, content):
    with open(destination,'wb') as FILE:
        FILE.write(content)

def main():
    module = AnsibleModule(
        argument_spec = dict(
            mode = dict(required=True, type='str'),
            source = dict(required=True, type='str', aliases=['src']),
            destination = dict(required=False, type='str', aliases=['dest']),
            host = dict(required=False, type='str'),
            user = dict(required=False, type='str'),
            api_token = dict(required=False, type='str', no_log=True, aliases=['access_token']),
            overwritten = dict(required=False, type='str', default='always', aliases=['force']),
            ssl_mode = dict(required=False, type='str', default='https', choices=['https', 'http', 'skip'])
        )
    )

    nc = NextcloudHandler(module.params)

    mode = module.params.get("mode")
    source = module.params.get("source")
    destination = module.params.get("destination")
    overwritten = module.params.get("overwritten")

    if mode == "get":
        if destination is None:
            raise AnsibleError('No destination is given')

        change = False
        r = nc.get("remote.php/dav/files/{USER}/{SRC}".format(USER=nc.user(), SRC=source))
        if overwritten == 'always':
            change = True
            write_file(destination, r.content)

        elif overwritten == 'different':
            change = False
            if os.path.isfile(destination):

                # md5sum local file
                local = hashlib.md5()
                with open(destination, "rb") as FILE:
                    for chunk in iter(lambda: FILE.read(4096), b""):
                        local.update(chunk)

                # md5sum remote file
                remote = hashlib.md5(r.content)
                
                if remote.hexdigest() != local.hexdigest():
                    change = True
                    write_file(destination, r.content)
            else:
                write_file(destination, r.content)

    elif mode == "delete":            
        r, change = nc.delete("remote.php/dav/files/{USER}/{SRC}".format(USER=nc.user(), SRC=source))

    elif mode == "put":
        r, change = nc.put("remote.php/dav/files/{USER}/{DEST}".format(USER=nc.user(), DEST=destination),
                            source)


    module.exit_json(changed = change, file={'destination': destination, 'mode': mode, 'source': source})
    

if __name__ == '__main__':
    main()