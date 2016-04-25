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


Constraint Checker
------------------

The ``IConstraintChecker`` utility is used to check if a transaction can be
executed on an object or not.

It's possible to register multiple ``IConstraintChecker`` utilities and all
utilities will be executed.

Adding an IConstraintChecker utility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create your Utility:

.. code:: python

    from ftw.statusmap.interfaces import IConstraintChecker
    from zope.interface import implements


    class MyConstraintCheckerUtility(object):
        implements(IConstraintChecker)

        def is_transition_allowed(self, obj, transition):
            return True

Register your utility in zcml.

.. code:: xml

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:i18n="http://namespaces.zope.org/i18n"
        i18n_domain="ftw.statusmap">

        <utility
          provides="ftw.statusmap.interfaces.IConstraintChecker"
          name="My Constraint Checker"
          factory=".checker.MyConstraintCheckerUtility"
          />

    </configure>

Links
-----

- Github: https://github.com/4teamwork/ftw.statusmap
- Issues: https://github.com/4teamwork/ftw.statusmap/issues
- Pypi: http://pypi.python.org/pypi/ftw.statusmap
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.statusmap


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.statusmap`` is licensed under GNU General Public License, version 2.
