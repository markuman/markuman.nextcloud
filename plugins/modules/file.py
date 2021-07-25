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
      - one of [always, never, different, different_size].
      - 'different' depends on md5sum an is made 'in memory' for remote files.
    default: 'always'
    aliases: ['force', 'overwritten']
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
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import parameter_spects
import os.path
import hashlib

def write_file(destination, content):
    with open(destination,'wb') as FILE:
        FILE.write(content)

def create_remote_md5sum_in_memory(nc, remote_file):
    r = nc.get("remote.php/dav/files/{USER}/{SRC}".format(USER=nc.user(), SRC=remote_file))
    return hashlib.md5(r.content).hexdigest(), r.content

def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec = parameter_spects(
            dict(
                mode = dict(required=True, type='str'),
                source = dict(required=True, type='str', aliases=['src']),
                destination = dict(required=False, type='str', aliases=['dest']),
                overwrite = dict(required=False, type='str', default='always', aliases=['force', 'overwritten']),
                delete_recursively = dict(required=False, type='bool', default=False)
            ))
        )


    nc = NextcloudHandler(module.params)

    mode = module.params.get("mode")
    source = module.params.get("source")
    destination = module.params.get("destination")
    overwrite = module.params.get("overwrite")
    delete_recursively = module.params.get("delete_recursively")

    message = "Undefined."
    change = False

    if mode == "get":
        facts = nc.propfind("remote.php/dav/files/{USER}/{SRC}".format(USER=nc.user(), SRC=source))

        if destination is None:
            raise AnsibleError('No destination is given')

        if facts == {}:
            message = "Requested file does not exist."
        else:
            r = nc.get("remote.php/dav/files/{USER}/{SRC}".format(USER=nc.user(), SRC=source))
            if overwrite == 'always' or not os.path.isfile(destination):
                change = True
                message = "File not received because of check_mode."
                if not module.check_mode:
                    write_file(destination, r.content)
                    message = "File received"

            elif overwrite == 'different':
                # md5sum local file
                local = hashlib.md5()
                with open(destination, "rb") as FILE:
                    for chunk in iter(lambda: FILE.read(4096), b""):
                        local.update(chunk)

                # md5sum remote file
                remote = hashlib.md5(r.content)
                message = "md5sum of dest and src is equal."
                if remote.hexdigest() != local.hexdigest():
                    change = True
                    message = "md5sum of dest and src is not equal. But file was not written due check_mode."
                    if not module.check_mode:
                        write_file(destination, r.content)
                        message = "File received. md5sum of dest and src was not equal."

            elif overwrite == 'different_size':
                message = "size of dest and src is equal."
                if os.path.getsize(destination) != facts.get('size'):
                    message = "size of dest and src is equal. But file was not written due check_mode"
                    change = True
                    if not module.check_mode:
                        write_file(destination, r.content)
                        message = "File received. Size of dest and src aws not equal."


    elif mode == "delete":
        facts = nc.propfind("remote.php/dav/files/{USER}/{SRC}".format(USER=nc.user(), SRC=source))
        message = "File does not already exists."
        if facts != {}:
            if not module.check_mode:
                if delete_recursively:
                    r, change = nc.delete("remote.php/dav/files/{USER}/{SRC}".format(USER=nc.user(), SRC=source))
                    if facts.get('content_type') != 'inode/directory':
                        message = "File deleted."
                    else:
                        message = "Folder deleted recurively."
                elif facts.get('content_type') != 'inode/directory':
                    r, change = nc.delete("remote.php/dav/files/{USER}/{SRC}".format(USER=nc.user(), SRC=source))
                    message = "File deleted"
                else:
                    message = "Cannot delete folder without set delete_recursively to true."
            else:
                message = "File not deleted due check_mode."
                change = True

    elif mode == "put":
        facts = nc.propfind("remote.php/dav/files/{USER}/{SRC}".format(USER=nc.user(), SRC=destination))
        if overwrite == 'always' or facts == {}:
            if not module.check_mode:
                r, change = nc.put("remote.php/dav/files/{USER}/{DEST}".format(USER=nc.user(), DEST=destination),
                                    source)
                message = "File uploaded."
            else:
                message = "File not uploaded due check_mode."
                change = True

        elif overwrite == 'different_size':
            message = "File not uploaded because size of dest and src is equal."
            if os.path.getsize(source) != facts.get('size'):
                if not module.check_mode:
                    r, change = nc.put("remote.php/dav/files/{USER}/{DEST}".format(USER=nc.user(), DEST=destination),
                                source)
                    message = "File was uploaded. Size of dest and src was not equal."
                else:
                    message = "File not uploaded due check_mode. Size of dest and src is not equal."
                    change = True



    module.exit_json(changed = change, file={'destination': destination, 'mode': mode, 'source': source}, message=message)
    

if __name__ == '__main__':
    main()