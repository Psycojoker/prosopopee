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
virtualenv ve
source ve/bin/activate
```

2. Download and install Prosopopee

```
pip install git+https://github.com/Psycojoker/prosopopee
```

## Files organisation

The files organisation is quite simple:

* in the root directory of your project you need a settings.yaml file that will contains the title and subtitle of your gallery
* for each gallery you'll need a folder that also contains a settings.yaml file that will describe how to display the content on your gallery

### Root settings.yaml

The root settings.yaml should contains 2 keys : one for the title of your website and one for the subtitle. It should looks like that:

```
title: My exploration of the outside world
sub_title: it's a scary place, don't go there
```

### Gallery settings.yaml

This settings.yaml will describe:

* the title, subtitle and cover picture of your gallery that will be used on the homepage
* if your gallery is public
* the date of your gallery: this will be used on the homepage since **galleries are sorted anti chronologically** on it
* the list of sections that will contains your gallery. A section will represent either one picture, a group of pictures or text.

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

And here is an example or a **private** gallery (notice the <code>public</code> keyword):

```yaml
title: Gallery title
sub_title: Gallery sub-title
date: 2016-01-15
cover: my_cover_picture.jpg
public: false
sections:
    - ...
```

## Build the website

**Note: You need to be in an activated virtualenv.**

In a folder containing the **root** settings.yaml file, simply do

    prosopopee

A `build` folder will be created in the current directory, containing an
index.html, static files (css & js) and pictures.

## Credit

> 16:57 &lt;meornithorynque> et tu as besoin d'un nom ?<br>
> 16:57 &lt;meornithorynque> genre n'importe quoi ?<br>
> 16:57 &lt;meornithorynque> je propose "Prosopopée"
