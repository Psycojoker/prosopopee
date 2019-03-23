Installation
============

Requirements
-------------

Ubuntu/Debian
~~~~~~~~~~~~~

We need Python, pip and virtualenv::

    apt-get install python-pip python-virtualenv

and graphicsmagick library for building the gallery::

    # graphicsmagick requires to have the 5.3.1 version of gcc-5-base
    apt-get install graphicsmagick

A video converter like ffmpeg::

    apt-get install ffmpeg

or::

    apt-get install libav-tools

For deployment, we need rsync::
  
    apt-get install rsync

Mac
~~~

We need Brew::

  /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

and graphicsmagick library for building the gallery::

  brew install graphicsmagick 
  
A video converter like ffmpeg::  
  
  brew install ffmpeg

For deployment, we need rsync::

  brew install rsync

Installation in virtualenv
--------------------------

1. Create a virtualenv, and activate it::

    virtualenv ve
    source ve/bin/activate

2. Download and install Prosopopee::

    pip install prosopopee
   
Docker
------

Get the Docker image::

    docker pull beudbeud/prosopopee
    
Run::

    docker run --rm -v $(pwd):/site prosopopee
    
More informations https://hub.docker.com/r/beudbeud/prosopopee/
