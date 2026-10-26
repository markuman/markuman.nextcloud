# markuman.nextcloud

[![CI](https://github.com/markuman/markuman.nextcloud/actions/workflows/ci.yml/badge.svg)](https://github.com/markuman/markuman.nextcloud/actions/workflows/ci.yml)
[![Galaxy](https://img.shields.io/badge/galaxy-markuman.nextcloud-blue)](https://galaxy.ansible.com/ui/repo/published/markuman/nextcloud/)

Ansible collection that brings your Nextcloud usage to the next level 🚀

* **modules and plugins** - automate files, users, talk, passwords and S3 buckets through the Nextcloud APIs. No ssh required.
* **install role** - set up Nextcloud on Debian 13 with nginx and ModSecurity. ssh required.

## Content

| | name | |
| --- | --- | --- |
| 💾 | `file`, `file_info` | download, upload and delete files, file and folder properties |
| 🛈 | `info` | version and capabilities of the server |
| 👥 | `user`, `user_info` | enable and disable users, user details |
| 🗨 | `talk` module + callback | post messages, or the results of a whole playbook, to a talk conversation |
| 🔑 | `password`, `password_info`, `passwords` lookup, `generate_password` lookup | [passwords app](https://apps.nextcloud.com/apps/passwords), including client side encryption |
| 🪣 | `s3_bucket`, `s3_bucket_info`, `s3_buckets` lookup | buckets and access keys of the [S3 API app](https://apps.nextcloud.com/apps/s3_api) |
| 🛠 | `nextcloud` role | install Nextcloud on Debian 13 |

## Install

```sh
ansible-galaxy collection install markuman.nextcloud
# or from git
ansible-galaxy collection install git+https://github.com/markuman/markuman.nextcloud.git
```

Requires ansible-core >= 2.17 and the python library `requests`.
`pysodium` is only needed for passwords with client side encryption.

## Usage

Authenticate with an app password. All modules are part of the action group `markuman.nextcloud.nextcloud`:

```yml
- hosts: localhost
  module_defaults:
    group/markuman.nextcloud.nextcloud:
      host: cloud.example.com
      user: ansible
      api_token: "{{ app_password }}"

  tasks:
    - name: upload a file if it changed
      markuman.nextcloud.file:
        mode: put
        src: /etc/hosts
        dest: backup/hosts
        overwrite: different

    - name: S3 bucket with a key for the backup client
      markuman.nextcloud.s3_bucket:
        name: backup
        folder: /S3/backup
        create_folder: true
        access_keys:
          - label: restic
            permission: readwrite
      register: bucket
      no_log: true

    - name: keep the secret in the passwords app
      markuman.nextcloud.password:
        name: s3-backup-restic
        username: "{{ item.access_key }}"
        password: "{{ item.secret_key }}"
        url: "{{ bucket.endpoint_url }}"
      loop: "{{ bucket.created_keys }}"
      no_log: true

    - name: all buckets
      ansible.builtin.debug:
        msg: "{{ query('markuman.nextcloud.s3_buckets') }}"
```

The connection can also be set with the env variables `NEXTCLOUD_HOST`, `NEXTCLOUD_USER`, `NEXTCLOUD_TOKEN` and `NEXTCLOUD_SSL_MODE`.
Lookup and callback plugins don't use `module_defaults`, they take the options directly or the env variables.

## Documentation

* [Wiki](https://github.com/markuman/markuman.nextcloud/wiki) - all modules, plugins and the role with examples
* `ansible-doc markuman.nextcloud.<module>`, e.g. `ansible-doc markuman.nextcloud.s3_bucket`
* `ansible-doc -t lookup markuman.nextcloud.s3_buckets`
* `ansible-doc -t role markuman.nextcloud.nextcloud`
* [Changelog](CHANGELOG.rst)

## Install role

| Collection | OS | Nextcloud | PHP | MariaDB | Webserver | EOL |
| --- | --- | --- | --- | --- | --- | --- |
| <= 9 | Ubuntu 20.04 | <= 23 | 7.4 | 10.3 | caddy | 2022.12 |
| <= 28 | Ubuntu 22.04 | <= 28 | 8.1 | 10.6 | caddy | 2024.09 |
| <= 29 | Ubuntu 24.04 | <= 29 | 8.3 | 10.11 | caddy | 2026.09 |
| >= 35 | Debian 13 | >= 35 | 8.4 | 11.8 | nginx + ModSecurity | 2028.08 |

See the [role README](roles/nextcloud/README.md) or the [wiki](https://github.com/markuman/markuman.nextcloud/wiki/install-role).

## Development

```sh
ansible-galaxy collection install -r tests/requirements.yml
```

| command | |
| --- | --- |
| `make sanity` | `ansible-test sanity` |
| `make lint` | `ansible-lint` |
| `make test` | module integration tests against the official nextcloud image (podman) |
| `make test-role` | install role in a Debian 13 systemd container + module integration tests against it (podman) |

GitHub Actions run sanity against ansible-core 2.17 to 2.22, ansible-lint, the integration tests and the role tests
on every push and pull request. The modules are tested against Nextcloud 35.

## Support

| host | |
| --- | --- |
| https://gitea.osuv.de/ansible-collections/markuman.nextcloud | origin |
| https://github.com/markuman/markuman.nextcloud | push mirror, pull requests and issues |
| https://gitlab.com/markuman/markuman.nextcloud | push mirror, merge requests and issues |
