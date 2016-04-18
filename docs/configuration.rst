Configuration
=============

Files organisation

The files organisation is quite simple:

 * in the root directory of your project you need a settings.yaml file that will contains the title and subtitle of your gallery
 * for each gallery you'll need a folder that also contains a settings.yaml file that will describe how to display the content on your gallery
 * and you put the pictures of the gallery inside the gallery folder

Root settings.yaml
------------------

The root settings.yaml should contains 2 keys : one for the title of your website and one for the subtitle. It should looks like that::

    title: My exploration of the outside world
    sub_title: it's a scary place, don't go there

It can also optionally contain a menu and global settings.`

Menu
____

It is possible to add a menu to your homepage that links to static pages. To do so, add a `menu` key to your `settings.yaml`, for example::

	menu:
  	  - about: "About"
  	  - first_gallery: "My first gallery"
  	  - http://twitter.com: "Twitter"

For example, this could be the content of `settings.yaml` in `about` folder::

	title: "About"
	static: true
	public: false
	sections:
	  - type: text
	    text: Some text, HTML <b>is allowed</b>.

You can use the `static` option to get a template closer to the one of the
homepage that is better suited for a static page. You'll need to specify
"public: false" if you don't want to list this page on the homepage. On you
case you didn't specified "public: false" you'll **need** to specify a "cover:"
entry like any other gallery.

**NOTE**: except the "static: " option to disepear quite soon for a more
generic approach to "choose your page style".

Global settings
_______________

Global settings can be set in your root `settings.yaml`, under the `settings` key.

GM
~~

Currently a `gm` settings key allows to customize the default GraphicsMagick's behavior. It looks like ::

	settings:
	  gm:
	    quality: 75
	    auto-orient: True
	    strip: True
	    resize: 50%

The meaning of the currently supported GraphicsMagick's settings is as follows :

 * `quality` allows to customize the compression level of thumbnails (between 0 and 100)
 * `auto-orient` change the orientation of pictures so they are upright (based on corresponding EXIF tags if present)
 * `strip` removes all profiles and text attributes from the image (good for privacy, slightly reduce file size)
 * `resize` can be used to resize the fullsize version of pictures. by default, input image size is preserved

Any GraphicsMagick setting can be customized on a per-image basis (either `cover` or `image`, see below).

Themes
~~~~~~

Prosopopée has a support for various themes. As for now, only 2 themes are available:

 * the default one called "exposure"
 * "material" based on materialcss

To specify the theme, add the "theme" key in your "settings" key or your
**root** settings.yaml. For example::

	title: My exploration of the outside world
	sub_title: it's a scary place, don't go there
	settings:
	  theme: material

Licence
~~~~~~~

By default Prosopopée use CC-BY-SA for all the content, if you want use a another licence 
you need add key in **root** settings.yaml. For example::

	licence:
	   name: WTFPL
	   url: "http://www.wtfpl.net/txt/copying/"

Share
~~~~~

If you want enable the share content on social network, add key in **root** settings.yaml. For example: 
By defaut you can share on facebook, twitter, pinterest, google+::

	share: true
	url: "http://prosopopee.com"

RSS
~~~

For activate the RSS you need add this key in **root** settings.yaml::

	rss: true
	url: "http://prosopopee.com"


Gallery settings.yaml
=====================

This settings.yaml will describe:

 * the title, subtitle and cover picture of your gallery that will be used on the homepage
 * the tags is optional
 * if your gallery is public (if not, it will still be built but won't appear on the homepage)
 * the date of your gallery: this will be used on the homepage since **galleries are sorted anti chronologically** on it
 * the list of sections that will contains your gallery. A section will represent either one picture, a group of pictures or text. The different kind of sections will be explained in the next README section.

Example
_______

::

	title: Gallery title
	sub_title: Gallery sub-title
	date: 2016-01-15
	cover: my_cover_picture.jpg
	tags:
	  - #yolo
	  - #travel
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

And here is an example or a **private** gallery (notice the <code>public</code> keyword)::

	title: Gallery title
	sub_title: Gallery sub-title
	date: 2016-01-15
	cover: my_cover_picture.jpg
	public: false
	sections:
	    - ...

