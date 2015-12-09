#!/usr/bin/python
# -*- coding:Utf-8 -*-

from setuptools import setup

setup(name='prosopopee',
      version='0.1',
      description='excposure.co clone in a static web generating tool',
      author='Laurent Peuch',
      #long_description='',
      author_email='cortex@worlddomination.be',
      url='https://github.com/Psycojoker/prosopopee',
      install_requires=open("./requirements.txt", "r").read().split(),
      packages=['prosopopee'],
      py_modules=[],
      license= 'GPLv3+',
      scripts=[],
      entry_points={
        'console_scripts': ['prosopopee = prosopopee.prosopopee:main']
      },
      keywords='',
      include_package_data=True,
      package_data={
            'prosopopee': ['static/css/*', 'static/js/*', 'static/img/*', 'templates/*.html', 'templates/sections/*'],
        },
     )
