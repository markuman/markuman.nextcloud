# Ansible Nextcloud Collection

Ansible Nextcloud Collection - is not meant to install nor to maintain your nextcloud itself.  
It's meant to bring up your nextcloud usage to the next level 🚀  
No ssh required.

### Features

[![Build Status](https://drone.osuv.de/api/badges/m/nextcloud_collection/status.svg)](https://drone.osuv.de/m/nextcloud_collection)

* 🔑 `lookup` plugin for [passwords app](https://apps.nextcloud.com/apps/passwords)
* 💾 `file` module - download, upload and delete files
* 🗨 `talk` module - post messages in conversations
* 👥 `user` module - maintain nextcloud users

### Support


| **host** | **category** |
| --- | --- |
| https://git.osuv.de/m/nextcloud_collection | origin |
| https://gitlab.com/markuman/nextcloud_collection | pull mirror, merge-requests and Issues |
| https://github.com/markuman/nextcloud_collection | push mirror, pull-requests and Issues |

# Usage

## Install

https://galaxy.ansible.com/markuman/nextcloud

`ansible-galaxy collection install markuman.nextcloud`

## Auth

You can authenticate either with your user password or with an App-Token (_Settings -> Security -> "Create new app password_).  
When you've setup MFA/2FA/TOTP, you must authenticate with an App-Token.

The collection modules and plugins require the following parameter. Alternatively the parameter can also be set as an ENV variable.

| **Ansible Parameter** | **ENV Variable** |
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

## file module

The `file` module supports also `access_token` as an alias for `api_token`, to be closer on ansible S3 module.

**mode: get**
```yml
- name: fetch file from nextcloud
  markuman.nextcloud.file:
    mode: get
    src: anythingeverything.jpg
    dest: /tmp/anythingeverything.jpg
    overwritten: different # 'always' is the default. 'never' is an option too.
    host: nextcloud.tld
    user: myuser
    api_token: xxx
```

**mode: delete**

CAUTION ⚠ removes files and folders - recursive!

```yml
- name: delete file on nextcloud
  markuman.nextcloud.file:
    mode: delete
    src: bla.docx
```

**mode: put**

```yml
- name: upload file on nextcloud
  markuman.nextcloud.file:
    mode: put
    src: /tmp/testtt.jpg
    dest: testtt.jpg
```

## talk module

```yml
- name: send hello
  markuman.nextcloud.talk:
    msg: Ho Hi from Ansible.
    channel: 8fyrb4ec
```

## user_info

List all nextcloud users.

```yml
- name: get nc users
  markuman.nextcloud.user_info:
  register: out

- debug: msg="{{ out.users }}"
```
