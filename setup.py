from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='nfg.ideal',
      version=version,
      description="Python class for iDEAL",
      long_description="""\
a simple python wrapper for the Mollie.nl webservice, a micropayment broker for the iDEAL system""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ideal nfg mollie',
      author='NFG Net Facilities Group BV',
      author_email='support@nfg.nl',
      url='http://www.nfg.nl',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
