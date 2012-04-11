#!/usr/bin/env python

from setuptools import setup

setup(name='fluidinfo.py',
      version='1.2.0',
      description="A thin wrapper for Fluidinfo's RESTful API",
      author='Nicholas Tollervey (based upon work by Sanghyeon Seo)',
      author_email='ntoll@ntoll.org',
      url='http://fluidinfo.com',
      py_modules=['fluidinfo',],
      license='MIT',
      install_requires=['requests',],
      long_description=open('README.rst').read(),
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Database',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries']
)
