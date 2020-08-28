# nextcloud_collection

Ansible Nextcloud Collection.  
https://galaxy.ansible.com/markuman/nextcloud

### SCM

| **host** | **category** |
| --- | --- |
| https://git.osuv.de/m/nextcloud_collection | origin |
| https://gitlab.com/markuman/nextcloud_collection | pull mirror |
| https://github.com/markuman/nextcloud_collection | push mirror |

### Features

* 🔑 `lookup` plugin for [passwords app](https://apps.nextcloud.com/apps/passwords)
    * status: draft
* 💾 `file` module to download, upload and delete files
    * status: todo
* 🗨 `talk` module to post messages in conversations
    * status: todo

# Usage

## Install

https://galaxy.ansible.com/markuman/nextcloud

`ansible-galaxy collection install markuman.nextcloud`

## lookup passwords

```yml
- name: Retrieve Password with label "Stackoverflow"
  debug:
    var: lookup('markuman.nextcloud.passwords', 'Stackoverflow' , host='nextcloud.tld', user='ansible', api_token='some-token')
```