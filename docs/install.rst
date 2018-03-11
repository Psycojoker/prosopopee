Installation
============

Requirements
-------------

Ubuntu/Debian
~~~~~~~~~~~~~

Installation needs Python, pip and virtualenv::

    apt-get install python-pip python-virtualenv

Gallery building needs graphicsmagick library::

    # graphicsmagick need to have a version of gcc-5-base in 5.3.1
    apt-get install graphicsmagick

An video convertor like ffmpeg::

    apt-get install ffmpeg

or::

    apt-get install libav-tools

The deployment need rsync::
  
    apt-get install rsync

Mac
~~~

Installation needs Brew::

  /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"


Gallery building needs graphicsmagick library::

  brew install graphicsmagick 
  

An video convertor like ffmpeg::  
  
  brew install ffmpeg

The deployment need rsync::

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
