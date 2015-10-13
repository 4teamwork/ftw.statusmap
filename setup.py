from setuptools import setup, find_packages
import os

version = '1.1.2.dev0'
maintainer = "Timon Tschanz"

tests_require = [
    'ftw.builder',
    'ftw.testbrowser',
    'ftw.testing',
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
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw statusmap plone workflow tree',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.statusmap',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
          'Plone',
          'Products.CMFCore',
          'Products.statusmessages',
          'setuptools',
          'plone.api',

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
