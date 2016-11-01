Example
=======

As a recap, here is how the files of the example gallery are organised::

	example
	      ├── settings.yaml
	      └── first_gallery
	          ├── settings.yaml
	          └── stuff.png

The content of ``example/settings.yaml``::

	title: "Example gallery"
	sub_title: some subtitle

The content of ``example/first_gallery/settings.yaml``::

	title: my first gallery
	sub_title: some subtitle
	date: 2015-12-08
	cover: stuff.png
	sections:
	  - type: full-picture
	    image: stuff.png
	    text:
	      title: Beautiful Title
	      sub_title: pouet pouet
	      date: 2015-12-08
	  - type: bordered-picture
	    image: stuff.png
	  - type: text
	    text: « voici plein de blabla à rajouter et <b>ceci est du gras</b> et encore plein plein plein plein de text car je veux voir comment ça va wrapper car c'est important et il faut pas que j'oublie de mettre des margins en % sinon ça va pas le faire alala là ça devrait aller »
	  - type: pictures-group
	    images:
	      -
	        - stuff.png
	        - stuff.png
	        - stuff.png
	      -
	        - stuff.png
	        - stuff.png
	  - type: full-picture
	    image: stuff.png

The content of ``example/second_gallery/settings.yaml``::
    
    title: my second level gallery
    sub_title: some subtitle
    date: 2015-12-08
    cover: stuff.png
    
The content of ``example/second_gallery/second_level_gallery_2/settings.yaml``::
    
    title: my second level gallery 2
    sub_title: some subtitle
    date: 2015-12-08
    cover: stuff.png
    sections:
      - type: full-picture
        image: stuff.png
        text:
          title: Beautiful Title
          sub_title: pouet pouet
          date: 2015-12-08
      - type: full-picture
        image:
          name: video.mp4
          type: video
        text:
          title: Beautiful Title
          sub_title: pouet pouet
          date: 2015-12-08
      - type: bordered-picture
        image:
          name: video.mp4
          type: video
      - type: bordered-picture
        image: stuff.png
      - type: bordered-picture
        image:
          name: video.mp4
          type: video
        text: "plop"
      - type: bordered-picture
        image: stuff.png
        text: "plop"
      - type: text
        text: « voici plein de blabla à rajouter et <b>ceci est du gras</b> et encore plein plein plein plein de text car je veux voir comment ça va wrapper car c'est important et il faut pas que j'oublie de mettre des margins en % sinon ça va pas le faire alala là ça devrait aller »
      - type: pictures-group
        images:
          -
            - name: stuff.png
              text: "test"
            - name: video.mp4
              type: video
            - name: stuff.png
              text: "test"
          -
            - stuff.png
            - name: video.mp4
              type: video
      - type: pictures-group
        images:
          -
            - name: stuff.png
              text: "test"
            - name: stuff.png
              text: "test"
            - name: stuff.png
              text: "test"
          -
            - stuff.png
            - stuff.png
      - type: full-picture
        image: stuff.png
      - type: full-picture
        image:
          name: video.mp4
          type: video
