================================
markuman nextcloud Release Notes
================================

.. contents:: Topics


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
