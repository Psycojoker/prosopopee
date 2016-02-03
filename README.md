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
* and you put the pictures of the gallery inside the gallery folder

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
* the list of sections that will contains your gallery. A section will represent either one picture, a group of pictures or text. The different kind of sections will be explained in the next README section.

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

### Different kind of sections

A gallery is compose of a succession of sections as you can on this [wonderfully
totally uninteresting example
gallery](http://psycojoker.github.io/prosopopee/first_gallery/) the gallery is
composed of 5 sections:

* a full screen picture with text written on it
* a picture with with borders around it
* a group of 5 pictures
* and a fullscreen picture without text on it this time

In your settings.yaml, a section will **always** have a <code>type</code> key
that will describe its kind and additional data. Underneath, the
<code>type</code> key is actually the name of an HTML template and the other
data will be passed to this template.

You can find all the sections templates here: https://github.com/Psycojoker/prosopopee/tree/master/prosopopee/templates/sections

You often have an <code>image</code> key. You need to give it a path to the
actual file. By convention, those files are put inside your gallery folder but
this is not mandatory.

#### Full Screen picture with OR without text on it

This display a full screen picture as shown in the [example
gallery](http://psycojoker.github.io/prosopopee/first_gallery/) in the first
and last sections. How you should use it:

With text:

```yaml
  - type: full-picture
    image: big_picture.jpg
    text:
      title: Big picture title
      sub_title: Some text
      date: 2016-01-15
```

Without text:

```yaml
  - type: full-picture
    image: big_picture.jpg
```

#### Bordered picture

This display a centered picture that is surrounded by white (the background) as
shown in the second position of the [example
gallery](http://psycojoker.github.io/prosopopee/first_gallery/).

How to use it:

```yaml
  - type: bordered-picture
    image: another_picture.jpg
```

#### Group of pictures

This display a group of zoomable pictures on one or multiple lines as shown on
the forth position (after the text) of the [example
gallery](http://psycojoker.github.io/prosopopee/first_gallery/).

```yaml
  - type: pictures-group
    images:
      -
        - image1.jpg
        - image2.jpg
        - image3.jpg
      -
        - image4.jpg
        - image5.jpg
```

Every sublist (the first level <code>-</code> represent a line).

**Know bug**: the images are left aligned, so if you don't put enough images on
a line, you'll have white space on the right.

#### Text

This display some centered text as shown on the third position of the [example
gallery](http://psycojoker.github.io/prosopopee/first_gallery/). HTML is
allowed inside the text.

How to use it:

```yaml
  - type: text
    text: Some text, HTML <b>is allowed</b>.
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
