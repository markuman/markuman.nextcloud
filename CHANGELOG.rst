================================
markuman nextcloud Release Notes
================================

.. contents:: Topics


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
