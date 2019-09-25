Changelog
=========

0.8.2 (2019-09-25)
 * Fix encryption page
 * Fix URI local (Thanks QShulz)

0.8.1 (2018-03-28)
 * Fix some css error
 * Update Material theme
 * Add fadeInUp effect in exposure theme

0.8 (2018-02-28)

 * Add night mode https://prosopopee.readthedocs.io/en/latest/configuration.html#night_mode
 * Add a test command to build html without generating media files
 * fix some bugs

0.7 (2017-10-04)

 * Add password access (based on https://robinmoisson.github.io/staticrypt/)

0.6 (2017-07-14)
 
 * Compatibility python 2 and 3
 * Possibility to add custom css and js http://prosopopee.readthedocs.io/en/latest/theming.html
 * Add reverse option by titoko https://prosopopee.readthedocs.io/en/latest/configuration.html#reverse

0.5 (2017-06-04)

 * Add audio HTML5 player https://prosopopee.readthedocs.org/en/latest/sections.html#audio by beudbeud
 * Update Material theme by beudbeud
 * Add iframe section https://prosopopee.readthedocs.org/en/latest/sections.html#iframe by beudbeud
 * Add quotes section https://prosopopee.readthedocs.org/en/latest/sections.html#quote by beudbeud
 * Add deploy and preview option https://prosopopee.readthedocs.io/en/latest/build.html#preview by beudbeud
 * Load only css and jss if the section is used by beudbeud
 * Possibility to add floating image in paragraph by beudbeud https://prosopopee.readthedocs.org/en/latest/sections.html#paragraph
 * fix some bugs

0.4 (2016-12-11)

 * greatly improved loading speed of pages with several different technics (see below)
 * RSS https://prosopopee.readthedocs.org/en/latest/configuration.html#rss by beudbeud
 * possibility to use video in section and cover by beudbeud (and a bit of Bram)
 * add lazyload for pics by beudbeud
 * if a theme doesn't have a section, fallback on exposure theme which is considered the default one by titoko
 * code and templates cleaning by Bram
 * make code a bit more robust by Bram
 * basic CI on travis by Bram
 * Light mode by beudbeud
 * progressive JPEG/GIF/PNG by default for a better loading experience by 0x010C following sebian's blogpost
 * <picture> element support for smoother loading by Bram
 * resposive mode of baguette by Bram
 * several background images for smoother loading by Bram
 * optimise write time to avoid blank pages during regeneration by Bram
 * optional opengraph support by beudbeud https://prosopopee.readthedocs.io/en/latest/configuration.html#open-graph-meta

0.3.1 (2016-04-13)

 * fix: cover date was hidden by default, this was a backward breaking behavior

0.3 the "beudbeud release" (2016-04-13)

 * caption support on bordered picture and pictures group https://prosopopee.readthedocs.org/en/latest/sections.html#advanced-options by beudbeud
 * configure licence https://prosopopee.readthedocs.org/en/latest/configuration.html#licence in footer by beudbeud
 * possibility to use a range for the full picture date https://prosopopee.readthedocs.org/en/latest/sections.html#full-screen-picture by beudbeud
 * Update material theme by beudbeud
 * social share https://prosopopee.readthedocs.org/en/latest/configuration.html#share by beudbeud
 * Define background and text color of section https://prosopopee.readthedocs.org/en/latest/sections.html#advanced-options by beudbeud

0.2 (2016-02-23)

 * a lot new contributors stepped in, see https://prosopopee.readthedocs.org/en/latest/authors.html
 * possibility to specify an (optional) menu https://prosopopee.readthedocs.org/en/latest/configuration.html#menu made by beudbeud
 * configure Graphics Magick options on a global or per images fashion https://prosopopee.readthedocs.org/en/latest/configuration.html#gm and https://prosopopee.readthedocs.org/en/latest/configuration.html#images-handling by capslock and jmk
 * support for various themes and a new material theme in addition of the default one https://prosopopee.readthedocs.org/en/latest/configuration.html#themes by beudbeud
 * tags support in gallery settings https://prosopopee.readthedocs.org/en/latest/configuration.html#example by beudbeud
 * introduce internal CACHE format version to avoid breaking build when changing it

0.1 (2016-02-09)

 * First pypi release

