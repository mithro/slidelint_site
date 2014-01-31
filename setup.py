import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'pyramid_zodbconn',
    'transaction',
    'pyramid_mailer',
    'ZODB',
    'chaussette',
    'docopt',
    'pyzmq',
    'hurry.filesize',
    ]

tests_requires = [
  'webtest',
  'testfixtures',
  'nose',
  'nose-selecttests',
  'coverage',
]

setup(name='slidelint_site',
      version='0.0',
      description='slidelint_site',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require={
          'tests': tests_requires,
          'develop': ['pylint'],
      },
      tests_require=requires + tests_requires,
      test_suite="slidelint_site",
      entry_points="""\
      [paste.app_factory]
      main = slidelint_site:main
      [console_scripts]
      slidelint_worker = slidelint_site.worker:worker_cli
      """,
      )
