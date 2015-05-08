ftw.statusmap
=============

A plone view listing objects and review states in a tree.

Features
--------

- Shows objects and review states recursively as tree.
- Adds CSS-classes per review-state for easy custom styling.
- Allows to execute workflow transitions for every object which has this transition available.

Usage
-----

- Add ``ftw.statusmap`` to your buildout configuration:

::

    [instance]
    eggs +=
        ftw.statusmap

- Install the generic setup profile.


Links
-----

- Main github project repository: https://github.com/4teamwork/ftw.statusmap
- Issue tracker: https://github.com/4teamwork/ftw.statusmap/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.statusmap
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.statusmap


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.statusmap`` is licensed under GNU General Public License, version 2.
