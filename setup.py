#!/usr/bin/python
# -*- coding:Utf-8 -*-

import os
from setuptools import setup
from operator import add

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst', format='md')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()


setup(name='prosopopee',
      version='0.2',
      description='exposure.co clone in a static web generating tool',
      author='Laurent Peuch',
      long_description=read_md('README.md') + "\n\n\n" + read_md('CHANGELOG'),
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
            'prosopopee': reduce(add, [[x[0].replace("prosopopee/", "", 1) + y for y in x[2]] for x in os.walk("prosopopee/themes/")], []),
        },
     )
