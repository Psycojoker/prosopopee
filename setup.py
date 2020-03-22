#!/usr/bin/python
# -*- coding:Utf-8 -*-

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='prosopopee',
      version='0.9.1',
      description='A static website generator that allows you to tell a story with your pictures',
      author='Laurent Peuch',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author_email='cortex@worlddomination.be',
      url='https://github.com/Psycojoker/prosopopee',
      install_requires=open("./requirements.txt", "r").read().split(),
      py_modules=[],
      license= 'GPLv3+',
      scripts=[],
      entry_points={
        'console_scripts': ['prosopopee = prosopopee.prosopopee:main']
      },
      keywords='',
      include_package_data=True,
      packages=['prosopopee'],
      package_dir={'prosopopee': 'prosopopee'},
      package_data={
            'prosopopee': ['themes/*/*/*/*', 'themes/*/templates/*.html', 'themes/*/templates/feed.xml', 'themes/*/templates/section/*.html'],
      },
)
