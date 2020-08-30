# nextcloud_collection

Ansible Nextcloud Collection - is not meant to install nor to maintain your nextcloud itself.  
It's meant to bring up your nextcloud usage to the next level ⭐⭐⭐
  * https://galaxy.ansible.com/markuman/nextcloud




### SCM

| **host** | **category** |
| --- | --- |
| https://git.osuv.de/m/nextcloud_collection | origin |
| https://gitlab.com/markuman/nextcloud_collection | pull mirror |
| https://github.com/markuman/nextcloud_collection | push mirror |

### Features

* 🔑 `lookup` plugin for [passwords app](https://apps.nextcloud.com/apps/passwords)
* 💾 `file` module to download, upload and delete files
    * status: work in progress
* 🗨 `talk` module to post messages in conversations
    * status: todo

# Usage

## Install

https://galaxy.ansible.com/markuman/nextcloud

`ansible-galaxy collection install markuman.nextcloud`

## Auth

You must authenticate with an app token. (Settings -> Security -> "Create new app password")

The collection modules and plugins require the following parameter (the parameter can also be set via ENV variable).

| **Parameter** | **ENV Variable** |
| --- | --- |
| `host` | `NEXTCLOUD_HOST` |
| `user` | `NEXTCLOUD_USER` |
| `api_token` | `NEXTCLOUD_TOKEN` |

## lookup passwords

```yml
- name: Retrieve Password with label "Stackoverflow"
  debug:
    var: lookup('markuman.nextcloud.passwords', 'Stackoverflow' , host='nextcloud.tld', user='ansible', api_token='some-token')
```