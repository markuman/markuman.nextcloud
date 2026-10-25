# Ansible Role: Nextcloud

This role installs and configures Nextcloud on a dedicated **Debian 13 (trixie)** server.

* php 8.4 (php-fpm)
* mariadb 11.8
* nginx with ModSecurity v3 and the OWASP Core Rule Set (including the nextcloud exclusions)
* let's encrypt certificates via certbot
* redis (file locking)
* coturn (talk)
* os and ssh hardening with `devsec.hardening`
* ufw and fail2ban

New installations get `nextcloud_version`. Updates of an existing installation are done with
the nextcloud updater or `occ upgrade`, the role never overwrites an existing installation.

## Requirements

* `ansible.mariadb`, `ansible.posix`, `community.general` and `devsec.hardening` collections
  (installed as dependencies of `markuman.nextcloud`)
* a DNS record of `nextcloud_fqdn` pointing to the server, for let's encrypt

## Role Variables

All variables are validated with `meta/argument_specs.yml`.

| Variable Name | Required | Default Value |
| --- | --- | --- |
| `nextcloud_fqdn` | yes | |
| `nextcloud_admin_user` | yes | |
| `nextcloud_admin_password` | yes | |
| `nextcloud_db_password` | yes | |
| `nextcloud_system_user` | yes | |
| `nextcloud_system_user_ssh_key` | yes | |
| `nextcloud_letsencrypt_mail` | with `nextcloud_tls_mode: letsencrypt` | |
| `nextcloud_version` | no | 35.0.2 |
| `nextcloud_tls_mode` | no | `letsencrypt` (or `selfsigned`) |
| `nextcloud_modsecurity_engine` | no | `On` (or `DetectionOnly`, `Off`) |
| `nextcloud_modsecurity_paranoia_level` | no | 1 |
| `nextcloud_max_upload_size` | no | 10G |
| `nextcloud_apps` | no | `[bruteforcesettings, twofactor_totp]` |
| `nextcloud_install_talk` | no | true |
| `nextcloud_install_media` | no | true |
| `nextcloud_install_redis` | no | true |
| `nextcloud_default_phone_region` | no | |
| `nextcloud_extra_config` | no | `{}` (`occ config:import` format) |
| `nextcloud_php_fpm.max_children`| no | 120 |
| `nextcloud_php_fpm.start_servers` | no | 12 |
| `nextcloud_php_fpm.min_spare_servers` | no | 8 |
| `nextcloud_php_fpm.max_spare_servers` | no | 40 |
| `nextcloud_opcache_interned_strings_buffer`| no | 16 |
| `nextcloud_innodb_buffer_pool_size` | no | 1G |
| `nextcloud_firewall` / `nextcloud_os_hardening` / `nextcloud_ssh_hardening` | no | true |

A full list of defaults and their values can be found in `defaults/main.yml`.

MariaDB `root@localhost` uses `unix_socket` authentication (Debian default), so there is no root password.

If modsecurity blocks legit requests, set `nextcloud_modsecurity_engine: DetectionOnly`
and check `/var/log/nginx/modsec_audit.log`.

### Upgrading from the Ubuntu/caddy based role (<= 29.x)

The role was rewritten for Debian 13 with nginx. Variables were renamed:

| old | new |
| --- | --- |
| `ubuntu_nextcloud_user` | `nextcloud_system_user` |
| `ubuntu_nextcloud_user_ssh_key_location` | `nextcloud_system_user_ssh_key` |
| `lets_encrypt_mail` | `nextcloud_letsencrypt_mail` |
| `mariadb_root_password` | removed (unix_socket auth) |
| `caddy_version` | removed (nginx from Debian) |
| `install_talk`, `install_media`, `install_redis` | `nextcloud_install_*` |
| `php_fpm`, `opcache.interned_strings_buffer` | `nextcloud_php_fpm`, `nextcloud_opcache_interned_strings_buffer` |
| `innodb_buffer_pool_size`, `remove_unused_authtokens_after_days` | `nextcloud_*` |
| `os_auditd_max_log_file_action`, `ssh_allow_users`, `ssh_max_auth_retries` | `nextcloud_*` |
| `ssh_kex`, `ssh_macs`, `ssh_ciphers` | removed, `devsec.hardening` defaults are used |

## Example Playbook

```yml
---
- hosts: my.cloud.tld
  become: true

  vars:
    nextcloud_system_user: some_ssh_user
    nextcloud_system_user_ssh_key: https://github.com/markuman.keys

    nextcloud_fqdn: my.cloud.tld
    nextcloud_letsencrypt_mail: my@cloud.tld

    nextcloud_db_password: some_random_nextcloud_database_password

    nextcloud_admin_user: admin
    nextcloud_admin_password: some_strong_password

  roles:
    - markuman.nextcloud.nextcloud
```

## Testing

`make test-role` in the collection root runs the role in a Debian 13 systemd container with podman
and executes the module integration tests against it (through nginx and modsecurity).
