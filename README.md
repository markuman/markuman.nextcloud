# Ansible Nextcloud Collection

Ansible Nextcloud Collection - is not meant to install nor to maintain your nextcloud itself.  
It's meant to bring up your nextcloud usage to the next level 🚀  
No ssh required.

## Features

* 💾 `file` module - download, upload and delete files
* 🗨 `talk` 
    * module - post messages in conversations
    * callback plugin - create deck cards or tasks of failing ansible tasks from talk
* 👥 `user_info` module - maintain nextcloud users
* ℹ `info` - collects information of nextcloud setup
* 🔑 passwords
    * `lookup` plugin for [passwords app](https://apps.nextcloud.com/apps/passwords)
    * `password` module - create, update and delete [passwords](https://apps.nextcloud.com/apps/passwords)


## install

`ansible-galaxy collection install markuman.nextcloud`

## Documentation / Usage

* [Wiki](https://git.osuv.de/m/nextcloud_collection/wiki/Home)

## Support

| **host** | **category** |
| --- | --- |
| https://git.osuv.de/m/nextcloud_collection | origin |
| https://gitlab.com/markuman/nextcloud_collection | pull mirror, merge-requests and Issues |
| https://github.com/markuman/nextcloud_collection | push mirror, pull-requests and Issues |
