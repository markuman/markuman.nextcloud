================================
markuman nextcloud Release Notes
================================

.. contents:: Topics


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
