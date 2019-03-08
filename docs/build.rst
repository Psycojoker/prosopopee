Build the website
=================

Generate
--------

**Note: You need to be in an activated virtualenv.**

In a folder containing the **root** settings.yaml file, simply do::

    prosopopee

A `build` folder will be created in the current directory, containing an
index.html, static files (css & js) and pictures.

Preview
-------

In a root folder launch this command::

  prosopopee preview

Then, you can check your website at http://localhost:9000

Deployment
----------

Prosopopee can upload your website with rsync, to do so, run::

  prosopopee deploy

