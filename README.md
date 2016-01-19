# Prosopopee

More or less a small clone of exposure.co in form of a static generator.

## Requirements

Installation needs Python, pip and virtualenv

    apt-get install python-pip python-virtualenv

Gallery building needs graphicsmagick library

    apt-get install graphicsmagick

## Installation

1. Create a virtualenv, and activate it

```
virtualenv venv
source venv/bin/activate
```

2. Download and install Prosopopee

```
pip instal git+https://github.com/Psycojoker/prosopopee
```

## Usage

Note: You need to be in an activated virtualenv.

In a folder containing a proper settings.yaml file, simply do

    prosopopee

A `build` folder will be created in the current directory, containing an
index.html, static files (css & js) and pictures.

### Settings file

A `settings.yaml` file is required on each gallery folder.

Here is an example:

```yaml
title: Gallery title
sub_title: Gallery sub-title
date: 2016-01-15
cover: my_cover_picture.jpg
sections:
  - type: full-picture
    image: big_picture.jpg
    text:
      title: Big picture title
      sub_title: Some text
      date: 2016-01-15
  - type: pictures-group
    images:
      -
        - image1.jpg
        - image2.jpg
        - image3.jpg
      -
        - image4.jpg
        - image5.jpg
  - type: text
    text: Some text, HTML <b>is allowed</b>.
  - type: bordered-picture
    image: another_picture.jpg
```

## Credit

> 16:57 &lt;meornithorynque> et tu as besoin d'un nom ?<br>
> 16:57 &lt;meornithorynque> genre n'importe quoi ?<br>
> 16:57 &lt;meornithorynque> je propose "Prosopopée"
