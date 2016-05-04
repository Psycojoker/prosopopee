Installation
============

Requirements
-------------

Installation needs Python, pip and virtualenv::

    apt-get install python-pip python-virtualenv

Gallery building needs graphicsmagick library::

    apt-get install graphicsmagick

An video convertor like ffmpeg::

    apt-get install ffmpeg

or::
    
    apt-get install libav-tools

Installation in virtualenv
--------------------------

1. Create a virtualenv, and activate it::

	virtualenv ve
	source ve/bin/activate

2. Download and install Prosopopee::

	pip install prosopopee
