# Ansible Nextcloud Collection

Ansible Nextcloud Collection - that brings up your nextcloud usage to the next level 🚀  
  * No ssh required for module usage
  * Install role requires ssh

## Features

* 💾 `file` module - download, upload and delete files
* 🗨 `talk` 
    * module - post messages in conversations
    * callback plugin - create deck cards or tasks of failing ansible tasks from talk
* 👥 `user_info` module - maintain nextcloud users
* 🛈 `info` - collects information of nextcloud setup
* 🔑 passwords
    * `lookup` plugin for [passwords app](https://apps.nextcloud.com/apps/passwords)
    * `password` module - create, update and delete [passwords](https://apps.nextcloud.com/apps/passwords)
* `markuman.nextcloud.nextcloud` installation role - securely setup Nextcloud.

## install

`ansible-galaxy collection install markuman.nextcloud`

## Documentation / Usage

* [Wiki](https://github.com/markuman/markuman.nextcloud/wiki)
* `ansible-doc <module>`
    * e.g. `ansible-doc markuman.nextcloud.file`

## Support

| **host** | **category** |
| --- | --- |
| https://gitea.osuv.de/ansible-collections/markuman.nextcloud | origin |
| https://gitlab.com/markuman/markuman.nextcloud | push mirror, merge-requests and Issues |
| https://github.com/markuman/markuman.nextcloud | push mirror, pull-requests and Issues |


| Collection Version | Supported OS | Nextcloud Version | Collection EOL |
| --- | --- | --- | --- |
| 9 | Ubuntu 20.04 | 23 | 2022.12 |
| 10 | Ubuntu 22.04 | >= 25 | TBA |