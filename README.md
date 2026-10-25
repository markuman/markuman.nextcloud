# Ansible Nextcloud Collection

Ansible Nextcloud Collection - that brings up your nextcloud usage to the next level 🚀  
  * No ssh required for module usage
  * Install role requires ssh

## Features

* 💾 `file` module - download, upload and delete files
* 🛈 `file_info` module - information about files and folders
* 🗨 `talk` 
    * module - post messages in conversations
    * callback plugin - post the results of ansible tasks to a talk conversation
* 👥 `user` and `user_info` modules - enable/disable users and receive user information
* 🛈 `info` - collects information of nextcloud setup
* 🔑 passwords
    * `passwords` and `generate_password` lookup plugins for the [passwords app](https://apps.nextcloud.com/apps/passwords)
    * `password` and `password_info` modules - create, update, delete and read [passwords](https://apps.nextcloud.com/apps/passwords)
* `markuman.nextcloud.nextcloud` installation role - securely setup Nextcloud on Debian 13 with nginx and ModSecurity.

All modules are part of the `markuman.nextcloud.nextcloud` action group:

```yml
- hosts: localhost
  module_defaults:
    group/markuman.nextcloud.nextcloud:
      host: cloud.example.com
      user: ansible
      api_token: "{{ app_password }}"
  tasks:
    - markuman.nextcloud.file:
        mode: put
        src: /etc/hosts
        dest: hosts
```

The connection settings can also be set with the `NEXTCLOUD_HOST`, `NEXTCLOUD_USER`,
`NEXTCLOUD_TOKEN` and `NEXTCLOUD_SSL_MODE` environment variables.

## install

**From galaxy.ansible.com**  
`ansible-galaxy collection install markuman.nextcloud`

It's also possible to install this collection directly from SCM.  
`ansible-galaxy collection install git+https://github.com/markuman/markuman.nextcloud.git`

Python requirements: `requests`, and `pysodium` for passwords with client side encryption.

## Documentation / Usage

* [Wiki](https://github.com/markuman/markuman.nextcloud/wiki)
* `ansible-doc <module>`
    * e.g. `ansible-doc markuman.nextcloud.file`
* `ansible-doc -t role markuman.nextcloud.nextcloud`

## Development

| command | |
| --- | --- |
| `make sanity` | `ansible-test sanity` |
| `make lint` | `ansible-lint` |
| `make test` | module integration tests against the official nextcloud image (podman) |
| `make test-role` | install role in a Debian 13 systemd container + module integration tests against it (podman) |

## Support

| **host** | **category** |
| --- | --- |
| https://gitea.osuv.de/ansible-collections/markuman.nextcloud | origin |
| https://gitlab.com/markuman/markuman.nextcloud | push mirror, merge-requests and Issues |
| https://github.com/markuman/markuman.nextcloud | push mirror, pull-requests and Issues |


| Collection Version | Supported OS | Nextcloud Version | Collection EOL | PHP | Mariadb | Webserver |
| --- | --- | --- | --- | --- | --- | --- |
| <= 9 | Ubuntu 20.04 | <= 23 | 2022.12 | 7.4 | 10.3 | caddy |
| <= 28 | Ubuntu 22.04 | <= 28 | 2024.09 | 8.1 | 10.6 | caddy |
| <= 29 | Ubuntu 24.04 | <= 29 | 2026.09 | 8.3 | 10.11 | caddy |
| >= 35 | Debian 13 | >= 35 | 2028.08 | 8.4 | 11.8 | nginx + ModSecurity |

The modules are tested with ansible-core 2.21 against Nextcloud 35. They require ansible-core >= 2.17.
