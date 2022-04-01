# Ansible Role: Nextcloud

This role installs, and configures Nextcloud for Ubuntu 20.04.

* php7.4
* mariadb 10.3
* caddy
* coturn

For more information, read the project wiki page: https://git.osuv.de/ansible_collections/markuman.nextcloud/wiki/install-role

## Requirements

* devsec.hardening collection >= 7.14.0

## Role Variables

| Variale Name | Required | Default Value |
| --- | --- | --- |
| `ubuntu_nextcloud_user` | yes | |
| `ubuntu_nextcloud_user_ssh_key_location` | yes | |
| `nextcloud_fqdn` | yes | |
| `lets_encrypt_mail` | yes | |
| `mariadb_root_password` | yes | |
| `nextcloud_db_password` | yes | |
| `nextcloud_admin_user` | yes | |
| `nextcloud_admin_password` | yes | |
| `php_fpm.max_children`| no | 120 |
| `php_fpm.start_servers` | no | 12 |
| `php_fpm.min_spare_servers` | no | 6 |
| `php_fpm.max_spare_servers` | no | 18 |
| `opcache.interned_strings_buffer`| no | 16 |
| `innodb_buffer_pool_size` | no | 512M |


A full list of defaults and their values can be found in the `defaults/main.yml`.


## Example Playbook


```yml
---
- hosts: my.cloud.tld
  become: yes

  vars:
    ubuntu_nextcloud_user: some_ssh_user
    ubuntu_nextcloud_user_ssh_key_location: https://github.com/markuman.keys
    
    nextcloud_fqdn: my.cloud.tld
    lets_encrypt_mail: my@cloud.tdl
    
    mariadb_root_password: some_random_mysql_root_pws
    nextcloud_db_password: some_random_nextcloud_database_password
    
    nextcloud_admin_user: admin
    nextcloud_admin_password: some_strong_password

  roles:
    - markuman.nextcloud
```

