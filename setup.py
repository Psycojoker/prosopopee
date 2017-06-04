#!/usr/bin/python
# -*- coding:Utf-8 -*-

from setuptools import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst', format='md')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()


setup(name='prosopopee',
      version='0.5',
      description='exposure.co clone in a static web generating tool',
      author='Laurent Peuch',
      long_description=read_md('README.md') + "\n\n\n" + open('docs/changelog.rst').read(),
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
            'prosopopee': ['themes/*/*/*/*', 'themes/*/templates/*.html', 'themes/*/templates/feed.xml', 'themes/*/templates/section/*.html'],
        },
     )
