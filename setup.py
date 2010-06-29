#!/usr/bin/env python

from distutils.core import setup

setup(name='fluiddb.py',
      version='1.0.3',
      description="A thin wrapper for FluidDB's RESTful API",
      author='Nicholas Tollervey (based upon work by Sanghyeon Seo)',
      author_email='ntoll@ntoll.org',
      url='http://fluidinfo.com',
      py_modules=['fluiddb',],
      license='MIT',
      long_description=open('README').read(),
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
