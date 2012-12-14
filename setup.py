from setuptools import setup, find_packages
import os

version = '1.0'
maintainer = "Timon Tschanz"

tests_require = [
    'unittest2',
    'ftw.testing',
    'plone.app.testing',
    ]


extras_require = {
    'tests': tests_require,
    }


long_description = (
    open('README.txt').read()
    + '\n' +
    open('docs/HISTORY.txt').read()
    + '\n')

setup(name='ftw.statusmap',
      version=version,
      description="A review state site map for plone.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        'Framework :: Plone',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.statusmap',
      license='gpl2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
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
