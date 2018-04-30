# Prosopopee

Prosopopee. Static site generator for your story.

Make beautiful customizable pictures galleries that tell a story using a static website generator written in Python. You don't need care about css, code and presentation, manage your contents in YAML file and Prosopopee will take care about the rest.

```yaml
title: Azerbaïdjan
date: 2015-12-18
cover: P1070043-01-01.jpeg
sections:
  - type: full-picture
    image: P1060979-01-01.jpeg
    fixed: true
    text:
      title: Azerbaïdjan
      sub_title: En décembre 2015 j'ai eu la chance de partir en Azerbaïdjan pour une mission professionnel pendant 10 jours.
      date: 2015-12-18
  - type: paragraph
    title: Baku
    text: Je n'ai pas eu beaucoup de temps pour visiter, mais j'ai quand même eu le temps de faire une visite de Baku et de rencontrer quelques habitants.<br>Baku est une ville très agréable, la vie est paisible. Par contre la ville n'est pas du tout prévu pour se déplacer à pied, ce qui ne m'a pas empêcher de me promener dans les rues de la vieille ville
  - type: pictures-group
    images:
      -
        - P1060938-01-01.jpeg
        - P1060946-01-01.jpeg
        - P1060947-01-01.jpeg
        - P1060948-01-01.jpeg
```

Prosopopee is sections oriented, make it very flexible, many kinds of section already available:

* Parallax
* Group of pics (gallery)
* Paragraph
* Iframe (Youtube, Maps, etc..)
* Quote
* [And more](http://prosopopee.readthedocs.io/en/latest/sections.html)

## Features

Prosopopee currently supports:

 * Lightweight
 * Thumbnails & multiple resolutions for fast previews (JPEG progressive)
 * Videos support
 * Mobile friendly
 * Caching for fast rendering
 * Multi level gallery
 * Support themes (default, material, light)
 * Password access (encrypt page)
 * Image lazy loading
 * Night Mode
 * Completely static output is easy to host anywhere
 * Hackable
 
 ## Examples
 
You can find example usages here:

* http://surleschemins.fr
* http://media.faimaison.net/photos/galerie/
* https://www.thebrownianmovement.org/
* http://outside.browny.pink
* http://such.life
* http://www.street-art.me
 
## TODO
 
 * More sections
 
 
## Usage
```bash
prosopopee
prosopopee preview
prosopopee deploy
prosopopee test
prosopopee (-h | --help)
prosopopee.py --version
```

## Docker

https://hub.docker.com/r/beudbeud/prosopopee/

## Licence 

GLPv3

## Documentation

  http://prosopopee.readthedocs.org/en/latest/

## IRC 

channel : irc.freenode.net#prosopopee

