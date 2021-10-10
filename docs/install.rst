Installation
============

Requirements
-------------

Ubuntu/Debian
~~~~~~~~~~~~~

We need Python, pip and virtualenv::

    apt-get install python3-pip python3-virtualenv

And a video converter like ffmpeg::

    apt-get install ffmpeg

or::

    apt-get install libav-tools

For deployment, we need rsync::
  
    apt-get install rsync

Mac
~~~

We need Brew::

  /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

And a video converter like ffmpeg::
  
  brew install ffmpeg

For deployment, we need rsync::

  brew install rsync

Installation in virtualenv
--------------------------

1. Create a virtualenv, and activate it::

    virtualenv ve
    source ve/bin/activate

2. Download and install Prosopopee::

    pip3 install prosopopee
   
Docker
------

Get the Docker image::

    docker pull beudbeud/prosopopee
    
Run::

    docker run --rm -v $(pwd):/site beudbeud/prosopopee
    
More informations https://hub.docker.com/r/beudbeud/prosopopee/
