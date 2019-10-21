from setuptools import setup, find_packages
import os

version = '1.5.1.dev0'

tests_require = [
    'unittest2',
    'plone.app.contenttypes',
    'plone.app.relationfield',
    'plone.app.testing',
    'plone.testing',
    'transaction',
    'zope.configuration',
    'ftw.builder',
    'ftw.testbrowser',
    'ftw.testing',
    'ftw.publisher.sender',
    'plone.api',
    'Products.DateRecurringIndex',
    ]


extras_require = {
    'tests': tests_require,
    }


setup(name='ftw.statusmap',
      version=version,
      description="A plone view listing objects and review states in a tree.",

      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.1',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw statusmap plone workflow tree',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.statusmap',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
          'Plone',
          'setuptools',
          'Products.CMFCore',
          'Products.statusmessages',
          'Zope2',
          'zope.i18nmessageid',
          'zope.publisher',
          'ftw.upgrade',
          # -*- Extra requirements: -*-
      ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
