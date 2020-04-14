import sys
import base64
from glob import glob
from jinja2 import Template
import ruamel.yaml as yaml
from path import Path


data = '''sections:
  - type: pictures-group
    images:
      -
{% set nb = namespace(value=range(2,5)|random) %}
{% set count = namespace(value=0) %}
{% for file in files %}
{% if count.value != nb.value %}
{% set file = file.split('/') %}
         - {{ file[-1] }}
{% set count.value = count.value + 1 %}
{% else %}
{% if not loop.last %}
      -
{% endif %}
{% set count.value = 0 %}
{% set nb. value = range(2,5)|random %}
{% endif %}
{% endfor %}
'''

def autogen(folder):
    gallery_settings = yaml.safe_load(open(Path(".").joinpath(folder, "settings.yaml").abspath(), "r"))

    types = ('*.JPG', '*.jpg', '*.JPEG', '*.jpeg')
    files_grabbed = []
    for files in types:
        files_grabbed.extend(glob(Path(".").joinpath(folder, files)))
    tm = Template(data, trim_blocks=True)
    msg = tm.render(title=gallery_settings['title'], date=gallery_settings['date'], cover=gallery_settings['cover'], files=files_grabbed)
    print(msg)
    f=open(Path(".").joinpath(folder, "settings.yaml").abspath(), "a")
    f.write(msg)
    return
