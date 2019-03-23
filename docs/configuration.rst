Configuration
=============

The files organisation is quite simple:

 * in the root directory of your project you need a settings.yaml file that contains the title and subtitle of your gallery
 * for each gallery you need a folder that also contains a settings.yaml file that describes how to display the content in your gallery
 * and you put the pictures of the gallery inside the gallery folder
 * or other directory, in the gallery became an index (so pictures won't be display, only cover of child gallery)

Root settings.yaml
------------------

The root settings.yaml should contain 2 keys: one for the title of your website and one for the subtitle. It should look like that::

    title: My exploration of the outside world
    sub_title: it's a scary place, don't go there

It can also optionally contain a menu and global settings.

Menu
____

It is possible to add a menu to your homepage that links to static pages. To do so, add a `menu` key to your `settings.yaml`, for example::

    title: "About"
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
"public: false" if you don't want to list this page on the homepage. If
you don't specify "public: false" you **need** to specify a "cover:"
entry like any other gallery.

**NOTE**: expect the "static: " option to disappear quite soon for a more
generic approach to "choose your page style".

Global settings
_______________

Global settings can be put in your root `settings.yaml`, under the `settings` key.

GM
~~

Currently a `gm` setting key allows to customize the default GraphicsMagick's behaviour. It looks like::

  title: Gallery
  settings:
    gm:
      quality: 75
      auto-orient: True
      strip: True
      resize: 50%
      progressive: True

The meaning of the currently supported GraphicsMagick's settings is as follows:

 * `quality` allows to customize the compression level of thumbnails (between 0 and 100)
 * `auto-orient` changes the orientation of pictures so they are upright (based on corresponding EXIF tags if present)
 * `strip` removes all profiles and text attributes from the image (good for privacy, slightly reduce file size)
 * `resize` can be used to resize the full-size version of pictures. By default, input image size is preserved
 * `progressive` converts classic baseline JPEG files to progressive JPEG, and interlaces PNG/GIF files (improves the page loading impression, slightly reduces file size)

Any GraphicsMagick setting can be customized on a per-image basis (either `cover` or `image`, see below).

Video converter
~~~~~~~~~~~~~~~

Prosopopée can use ffmpeg or libav and each can be configured if needed::

  title: Gallery
  settings:
    ffmpeg:
      binary: "ffmpeg"
      loglevel: "error"
      format: "webm"
      resolution: "1280x720"
      vbitrate: "3900k"
      abitrate: "100k"
      audio: "libvorbis"
      video: "libvpx"
      other: "-qmin 10 -qmax 42 -maxrate 500k -bufsize 1500k"

The meaning of the currently supported FFMEG or LIBAV's settings is as follows :

 * `binary` sets the binary to use to convert the video (ffmpeg or avconv)
 * `loglevel` sets the logging level used by the library
 * `format` forces input or output file format
 * `resolution` sets frame size
 * `vbitrate` sets video bitrate
 * `abitrate` sets audio bitrate
 * `audio` sets the audio codec
 * `video` sets the video codec
 * `extension` sets the extension of output file
 * `other` sets different options if you need more

example for MP4::

  title: Gallery
  settings:
    ffmpeg:
      binary: "ffmpeg"
      format: "mp4"
      audio: "acc"
      video: "libx264"
      extension: mp4

Light Mode
~~~~~~~~~~

To enable the light mode::

  title: Gallery
  settings:
    light_mode: true

With this option Prospopee makes a subdirectory with light version of your gallery. 
This light gallery uses less JS, pictures in low size, etc.

To access this light gallery, add /light at the end of the URL of the gallery.

If you want only light theme, see :ref:`themes`.

Night Mode
~~~~~~~~~~

To enable the night mode, which is only available for exposure theme (default theme)::

  title: Gallery
  settings:
    night_mode: true

After that you will be able to choose between dark theme or light theme when visiting the website.

.. themes:
Themes
~~~~~~

Prosopopée supports different themes. As for now, only 3 themes are available:

 * the default one called "exposure"
 * "material" based on materialcss
 * light 

To specify the theme, add the "theme" key in your "settings" key or your
**root** settings.yaml. For example::

  title: My exploration of the outside world
  sub_title: it's a scary place, don't go there
  settings:
    theme: material

Licence
~~~~~~~

By default Prosopopée uses CC-BY-SA for all the content. If you want to use another licence,
you need to add a "licence" key in **root** settings.yaml. For example::
 
  title: Gallery
  licence:
    name: WTFPL
    url: "http://www.wtfpl.net/txt/copying/"

Share
~~~~~

If you want to enable content sharing on social networks, add the "share" key in **root** settings.yaml. For example::

  title: Gallery
  share: true
  url: "http://prosopopee.com"

By default you can share on facebook, twitter, pinterest, google+.

RSS
~~~

To activate the RSS feed you need to add the "rss" key in **root** settings.yaml::

  title: Gallery
  rss: true
  url: "http://prosopopee.com"

Open Graph Meta
~~~~~~~~~~~~~~~

To activate the Open Graph Meta you need to add the "og" key in **root** settings.yaml::

  title: Sur les chemins
  settings:
    og: true

You can also specify a description and a language ("lang" key) for a gallery.

For more information about Open Graph http://ogp.me/

Deployment
~~~~~~~~~~

If you want to configure the deployment of your website with rsync::

  title: Gallery
  settings:
    deploy:
      ssh: true (optional, for ssh)
      username: username (optional, for ssh)
      hostname: server.com (optional, for ssh)
      dest: /var/www/website/build/
      others: --delete-after (optional)

Reverse order
~~~~~~~~~~~~~

Normally Prosopopee builds the gallery index in anti-chronological. If you want to have it in chronological order, use the "reverse" key::

    settings:
      reverse: true

This option can also be used in a gallery settings.yaml if you use multi-level galleries::

  title: Multi level gallery
  reverse: true

Password access
~~~~~~~~~~~~~~~

If you want to protect all the website by password::

  title: Gallery
  password: my_super_password

Gallery settings.yaml
---------------------

This settings.yaml will describe:

 * the title, subtitle and cover picture of your gallery that will be used on the homepage
 * the tags, which are optional
 * if your gallery is public (if not, it will still be built but won't appear on the homepage)
 * the date of your gallery that will be used on the homepage since **galleries are sorted anti-chronologically**
 * the list of sections that represents your gallery. A section represents either one picture, a group of pictures or text. The different kinds of sections will be explained in the next README section.

Example
_______

::

    title: Gallery title
    sub_title: Gallery sub-title
    date: 2016-01-15
    cover: my_cover_picture.jpg
    description: Some text
    lang: en_US
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

And here is an example of a **private** gallery (notice the ``public`` keyword)::

    title: Gallery title
    sub_title: Gallery sub-title
    date: 2016-01-15
    cover: my_cover_picture.jpg
    public: false
    sections:
        - ...

Advanced settings
-----------------

Image handling
_______________

Images go into the `cover` or `image` keys.
Each image individual processing settings can be customized to override the default
GraphicsMagick settings defined (or not) in the root `settings.yaml`.

This is done by putting the image path into a `name` key,
and adding specific processing settings afterwards.

For example, you can replace::

    image: image1.jpg

by::

    image:
      name: image1.jpg
      quality: 90
      strip: False
      auto-orient: False

Password access
_______________

You can restrict access to a gallery with a password::

    title: Gallery title
    sub_title: Gallery sub-title
    password: my_super_password

