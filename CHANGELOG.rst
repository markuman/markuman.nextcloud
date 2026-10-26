================================
markuman nextcloud Release Notes
================================

.. contents:: Topics

v35.0.0
=======

Release Summary
---------------

Major release after two years without updates. Tested against ansible-core 2.21 and Nextcloud 35.
The install role was rewritten for Debian 13 with nginx and ModSecurity.
The modules got a lot of bugfixes and the integration tests run with podman now.
The new ``s3_bucket`` and ``s3_bucket_info`` modules and the ``s3_buckets`` lookup manage buckets and access keys of the S3 API app.

Major Changes
-------------

- collection - requires ansible-core >= 2.17 and Python 3.
- nextcloud install role - rewritten for Debian 13 (trixie) with php 8.4, mariadb 11.8, nginx, ModSecurity v3 and the OWASP CRS. Ubuntu and caddy are no longer supported.

Minor Changes
-------------

- CI - GitHub Actions replace woodpecker. They run ``ansible-test sanity`` against ansible-core 2.17 to 2.22, ``ansible-lint``, the module integration tests and the role tests.
- all modules - ``InsecureRequestWarning`` is no longer printed with ``ssl_mode=skip``.
- all modules - ``host`` also accepts a full base url like ``https://example.com/nextcloud``.
- all modules - ``ssl_mode`` has choices and all connection options have env fallbacks (``NEXTCLOUD_HOST``, ``NEXTCLOUD_USER``, ``NEXTCLOUD_TOKEN``, ``NEXTCLOUD_SSL_MODE``).
- all modules - added ``RETURN`` documentation.
- all modules - use OCS v2 API endpoints, a requests session and timeouts. Error messages contain the http status and the message of nextcloud.
- file - ``mode`` and ``overwrite`` have choices now.
- file - ``overwrite=different`` works for ``mode=put`` as well.
- file - downloads are streamed to disk and moved atomically instead of being held in memory.
- file - uploads into a missing folder fail with a clear error message.
- integration tests - run with podman against the official nextcloud image, including talk, the talk callback and the s3_api app.
- lookup plugins - options are documented and can be set with ``NEXTCLOUD_*`` env variables.
- nextcloud install role - ModSecurity runs with the OWASP CRS nextcloud exclusions plus own exclusions for large webdav uploads (``SecRequestBodyLimitAction ProcessPartial``) and ``PUT``/``PATCH``/``DELETE`` on the OCS API. Use ``nextcloud_modsecurity_engine=DetectionOnly`` for tuning.
- nextcloud install role - argument specs for all variables.
- nextcloud install role - background jobs use cron mode.
- nextcloud install role - coturn secret is generated once and the turn server is only added once to talk. coturn denies private peer ips.
- nextcloud install role - mariadb settings are placed in ``mariadb.conf.d/90-nextcloud.cnf``, ``innodb_log_file_size`` is 256M and the slow query log is enabled.
- nextcloud install role - nextcloud configuration is applied idempotently with ``occ config:import``, apps are only installed if missing.
- nextcloud install role - nextcloud download is verified with gpgv against a dedicated keyring.
- nextcloud install role - nginx configuration follows the current nextcloud documentation and uses ``http2 on`` instead of the deprecated ``listen ... http2``.
- nextcloud install role - php-fpm uses an own ``nextcloud`` pool and php settings are placed in ``conf.d/90-nextcloud.ini`` instead of editing ``php.ini``.
- nextcloud install role - redis, fail2ban, php-fpm, nginx, mariadb, coturn and the certbot timer are explicitly started and enabled.
- nextcloud install role - runs ``occ maintenance:repair --include-expensive`` after a new installation.
- passwords lookup - supports multiple terms.
- role tests - ``make test-role`` runs the role in a Debian 13 systemd container and the module integration tests against it.
- talk - supports check mode.
- talk callback - options are documented (``NEXTCLOUD_TALK_CALLBACK_CHANNEL`` or ini) and errors are shown as warnings instead of breaking the playbook.

Breaking Changes / Porting Guide
--------------------------------

- collection - depends on ``ansible.mariadb`` instead of ``community.mysql`` and ``devsec.hardening`` >= 10.5.1.
- file_info - ``file_id``, ``size`` and ``favorite`` of folders are integers now (like for files).
- nextcloud install role - ``mariadb_root_password`` was removed, root uses ``unix_socket`` authentication. The ``devsec.hardening.mysql_hardening`` role is no longer used.
- nextcloud install role - ``ssh_kex``, ``ssh_macs`` and ``ssh_ciphers`` were removed, the defaults of ``devsec.hardening`` (including post-quantum key exchange) are used.
- nextcloud install role - all role variables have the ``nextcloud_`` prefix now, ``ubuntu_nextcloud_user`` is ``nextcloud_system_user``, ``ubuntu_nextcloud_user_ssh_key_location`` is ``nextcloud_system_user_ssh_key``, ``lets_encrypt_mail`` is ``nextcloud_letsencrypt_mail``. See the role README for the full list.
- nextcloud install role - an existing nextcloud installation is never overwritten by the role anymore. Use the nextcloud updater or ``occ upgrade``.
- password - ``favorite`` has no default anymore, an existing password keeps its favorite state when ``favorite`` is omitted.
- user - ``diff`` only contains the ``enabled`` state instead of the complete user as yaml.
- user - fails if the user does not exist instead of silently doing nothing.
- user_info - returns an empty ``users`` list and an empty ``user_data`` dict if the requested ``username`` does not exist.

Removed Features (previously deprecated)
----------------------------------------

- nextcloud install role - caddy support.

Bugfixes
--------

- all modules - a missing ``requests`` library led to a ``NameError`` instead of a useful error message.
- file - check mode reported a change when deleting a folder without ``delete_recursively``.
- file - file names with special characters like spaces, ``#`` or ``?`` were not url encoded.
- file - uploaded files were never closed.
- lookup plugins - errors were silently ignored because ``AnsibleError`` was created but never raised.
- nextcloud install role - ``ansible.builtin.ini_file`` does not exist, it is ``community.general.ini_file``.
- nextcloud install role - ``install_talk`` had no effect.
- nextcloud install role - ``libmagickcore-6.q16-6-extra`` is only a virtual package on Ubuntu 24.04 and broke the package installation.
- nextcloud install role - ``nextcloud_db_name`` and ``nextcloud_db_user`` had no effect.
- nextcloud install role - a new coturn secret was generated on every run and the turn server was added to talk again on every run.
- nextcloud install role - nextcloud was extracted over an existing installation on every run.
- nextcloud install role - redis was never explicitly started.
- password - ``favorite=false`` was sent as string ``False`` which the passwords app treated as ``true``.
- password - a folder was created in check mode.
- password - an update reset ``username``, ``url``, ``notes`` and ``favorite`` of the password because the passwords app resets all fields that are not sent.
- password - changes of ``username``, ``url``, ``notes``, ``favorite`` and ``folder`` of existing passwords were ignored.
- password - the generated password was sent as list.
- passwords lookup - only the first term was looked up.
- talk callback - did not call the ``CallbackBase`` constructor and ``v2_playbook_on_(not_)import_for_host`` crashed with a ``TypeError``.
- user - enabling or disabling a user failed because a method instead of the headers was handed to requests.

New Plugins
-----------

Lookup
~~~~~~

- s3_buckets - list the buckets of the nextcloud s3_api app

New Modules
-----------

- s3_bucket - manage buckets and access keys of the nextcloud s3_api app
- s3_bucket_info - info about buckets and access keys of the nextcloud s3_api app

v29.0.4
=======

Release Summary
---------------

Bump version of nextcloud and caddy.

v29.0.2
=======

Release Summary
---------------

This is the minor release of the ``markuman.nextcloud`` collection.

Minor Changes
-------------

- bump caddy to 2.8.0
- bump nextcloud to 29.0.1

Bugfixes
--------

- add trailing slash on well-known urls.
- richdocumentscode installation is only available for x86_64.

v29.0.0
=======

Release Summary
---------------

Version 29 and greate supports Ubuntu 24.04, PHP 8.3 and mariadb 10.11 only.

v28.0.1
=======

Release Summary
---------------

Bump nextcloud version to 28.0.3.

v28.0.0
=======

Release Summary
---------------

This is a major release of ``markuman.nextcloud`` in version 28. It installed nextcloud 28 now.

Minor Changes
-------------

- bump nextcloud to 28.0.0
- change sudoers configuration to ``/etc/sudoers.d/ubuntu_nextcloud_user`` to keep existing ``/etc/sudoers`` untouched
- dump caddy to 2.7.6
- install and configure redis is available now via ``install_redis`` variable. default is ``true``
- use ``defaults/main.yml`` for ssh hardening defaults

v27.0.0
=======

Release Summary
---------------

Major update of ``markuman.nextcloud``. Use nextcloud 27 and caddy 2.7.

v26.0.0
=======

Release Summary
---------------

With this release, the Collection Major Version is in sync with the Nextcloud Server Major Version.

v11.2.0
=======

Release Summary
---------------

Minor release. Just bump nextcloud to 25.0.5 and caddy to 2.6.4.

v11.1.0
=======

Release Summary
---------------

11.1.0 - big mariadb improvment.
Installation role will follow most of the mariadb recommendations now (https://docs.nextcloud.com/server/latest/admin_manual/configuration_database/linux_database_configuration.html#configuring-a-mysql-or-mariadb-database).
Furthermore, it will create a daily schedule event that will remove authtokens that aren't used for more than 21 days.

Minor Changes
-------------

- markuman.nextcloud.nextcloud - add a mariadb event scheduler that removes unused authtokens when their last usage is older than 21 days. The value can be overwritten with the variable ``remove_unused_authtokens_after_days``. A ``0`` value will disable the create of the event.
- markuman.nextcloud.nextcloud - enable mariadb ``query_cache``.
- markuman.nextcloud.nextcloud - enable mariadb event scheduler in general.
- markuman.nextcloud.nextcloud - increase mariadb ``max_heap_table_size``.
- markuman.nextcloud.nextcloud - increase mariadb ``tmp_table_size``.
- markuman.nextcloud.nextcloud - set linux user client characters also to utf8mb4.
- markuman.nextcloud.nextcloud - set mariadb transaction isolation to ``READ-COMMITTED``.

v11.0.1
=======

Release Summary
---------------

Trivial bugfix release.

Bugfixes
--------

- markuman.nextcloud.password_info - ``version_added`` for ``cse_password`` was wrong.

v11.0.0
=======

Release Summary
---------------

The ``password_info`` module and ``password`` lookup plugin supports end to end encryption now.

Minor Changes
-------------

- markuman.nextcloud.password_info - new parameter ``cse_password`` for end to end encryption.

Bugfixes
--------

- plugins/module_utils/nextcloud.py - fix wrong indentation in ``NextcloudErrorHandler``.

v10.2.0
=======

Release Summary
---------------

This minor release of ``markuman.nextcloud`` improves the security of the instance itself
and the installation process.

Minor Changes
-------------

- markuman.nextcloud.nextcloud - bump default nextcloud version to 25.0.3.
- markuman.nextcloud.nextcloud - include nextcloud public gpg key to verify nextcloud download before installation.
- markuman.nextcloud.nextcloud - install fail2ban for better sshd security.

v10.1.1
=======

Bugfixes
--------

- markuman.nextcloud.nextcloud - fix preview generator timer service.

v10.1.0
=======

Release Summary
---------------

This is the minor release of the ``markuman.nextcloud`` collection.

Minor Changes
-------------

- markuman.nextcloud.nextcloud - Install role can install and configure media setup (recognize, memories, previewgenerator, nextcloud office) via variable `install_media`. The default value is ``true``.

Bugfixes
--------

- markuman.nextcloud.nextcloud - Add missing https schema to ``overwrite.cli.url``.
- markuman.nextcloud.nextcloud - Entire installation role is now immutable.
- markuman.nextcloud.nextcloud - chown ``/var/log/caddy`` path for www-data.

v10.0.1
=======

Release Summary
---------------

Bump nextcloud version to 25.0.2

v10.0.0
=======

Release Summary
---------------

The install role supports now nextcloud 25 on ubuntu 22.04 only.

v9.3.0
======

Release Summary
---------------

Minor sanity fixes and update version for the install role.
This will also be the last 9.x.x release.

New Modules
-----------

- user - administrate nextcloud users

v9.2.2
======

Release Summary
---------------

bugfix release of ``markuman.nextcloud``.

Minor Changes
-------------

- nextcloud install role - dump caddy version to 2.5.1

v9.2.1
======

Release Summary
---------------

Bugfix release of ``markuman.nextcloud``.

Bugfixes
--------

- nextcloud installation role - add missing mail configuration in caddy web server.

v9.2.0
======

Release Summary
---------------

This is the minor release of the ``markuman.nextcloud`` collection.
This release affects only the installation role ``markuman.nextcloud.nextcloud``.

Minor Changes
-------------

- bump caddy version to 2.5.0
- bump nextcloud version to 23.0.4
- make coturn/talk installation controllable via boolean `install_talk` variable.

Bugfixes
--------

- coturn config location was wrong and results in error.

v9.1.1
======

Release Summary
---------------

This release of the ``markuman.nextcloud`` collection includes a turnkey-ready install role for Ubuntu 20.04 LTS.

Minor Changes
-------------

- add install role ``markuman.nextcloud`` to distribute a turnkey nextcloud on Ubuntu 20.04 LTS.

v9.0.2
======

Release Summary
---------------

This is the patch release of the ``markuman.nextcloud`` collection.
This changelog contains all changes to the modules and plugins in this collection
that have been made after the previous release.

Minor Changes
-------------

- file - replace md5 with sha256 when comparing files.
- passwords - Set no_log for ``update_password`` parameter.
- remove unused variables and imports

Bugfixes
--------

- Multiple ansible sanity fixes.
