================================
markuman nextcloud Release Notes
================================

.. contents:: Topics


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
