# nextcloud_collection

Ansible Nextcloud Collection - is not meant to install nor to maintain your nextcloud itself.  
It's meant to bring up your nextcloud usage to the next level 🚀

### Features

* 🔑 `lookup` plugin for [passwords app](https://apps.nextcloud.com/apps/passwords)
* 💾 `file` module to download, upload and delete files
* 🗨 `talk` module to post messages in conversations

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
    message: Ho Hi from Ansible.
    channel: 8fyrb4ec
```

### SCM

| **host** | **category** |
| --- | --- |
| https://git.osuv.de/m/nextcloud_collection | origin |
| https://gitlab.com/markuman/nextcloud_collection | pull mirror |
| https://github.com/markuman/nextcloud_collection | push mirror |
