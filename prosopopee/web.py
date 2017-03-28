import os
import yaml
from flask import Flask, render_template, send_file, request

from prosopopee import main as build_everything, get_settings

app = Flask("prosopopee")


@app.route("/build/")
def build_index():
    file = os.path.join(os.path.realpath(os.curdir), "build", "index.html")
    return send_file(file, cache_timeout=0)


@app.route("/build/<path:path>")
def build(path=""):
    file = os.path.join(os.path.realpath(os.curdir), "build", path)

    # I get a request for a gallery folder so I need to return the index.html
    if os.path.isdir(file):
        file = os.path.join(file, "index.html")

        # this is an horrible hack because iframe are broken
        # prosopopee uses relatives links everywhere, but the iframe doesn't
        # understand that, so if you click on a link inside the iframe, the
        # base link on which relatives paths are based on isn't updated for
        # whatever reason, so every related links are broken
        #
        # for example : on the demo gallery, load the root, requests are made on "/build/"
        # but if you click on the first_gallery, requests for the image in <img
        # src="1.png"> is going to be made on "/build/" while it should have
        # been made on "/build/first_gallery/"
        file = open(file, "r").read().decode("Utf-8").replace("<head>", u'<head><base href="%s/" _target="blank">' % path)

        print file
        return file.encode("Utf-8")

    if not os.path.exists(file):
        return ""

    return send_file(file, cache_timeout=0)


@app.route("/settings/build/")
def get_base_gallery_settings():
    return get_gallery_settings(".")


@app.route("/settings/build/<path:path>")
def get_gallery_settings(path):
    return open(os.path.join(path, "settings.yaml")).read()


@app.route("/save_settings/build/", methods=['POST'])
def save_base_settings():
    return save_settings(".")

@app.route("/save_settings/build/<path:path>", methods=['POST'])
def save_settings(path):
    # TODO error in yaml

    assert request.form["settings"]
    open(os.path.join(path, "settings.yaml"), "w").write(request.form["settings"])

    build_everything()

    return "ok"


@app.route("/new_gallery/", methods=["POST"])
def new_gallery():
    os.makedirs(request.form["folder_name"])
    settings = yaml.dump({
        "title": request.form["title"].encode("Utf-8"),
        "date": request.form["date"].encode("Utf-8"),
        "sections": [{
            "type": "full-picture",
            "image": "example.png",
            "text": {
                "title": request.form["title"].encode("Utf-8"),
                "date": request.form["date"].encode("Utf-8"),
            }
        }]
    }, default_flow_style=False)

    open(os.path.join(request.form["folder_name"], "settings.yaml"), "w").write(settings)

    return "ok"


@app.route("/upload_images/", methods=["POST"])
def upload_images():
    from ipdb import set_trace; set_trace()

""""
ipdb> request.form
ImmutableMultiDict([('path', u'/build/')])
ipdb> request.files
ImmutableMultiDict([('images', <FileStorage: u'C7tMVgBWkAEqbbz (1).jpg' ('image/jpeg')>), ('images', <FileStorage: u'C7tMVgBWkAEqbbz.jpg-large' ('application/octet-stream')>), ('images', <FileStorage: u'DettePubliqueFrancaise_gauche_vs_droite.jpg' ('image/jpeg')>)])
ipdb> request.files["images"]
<FileStorage: u'C7tMVgBWkAEqbbz (1).jpg' ('image/jpeg')>
ipdb> dir(request.files)
['__class__', '__cmp__', '__contains__', '__copy__', '__deepcopy__', '__delattr__', '__delitem__', '__dict__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__getstate__', '__gt__', '__hash__', '__init__', '__iter__', '__le__', '__len__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_hash_cache', '_iter_hashitems', 'add', 'clear', 'copy', 'deepcopy', 'fromkeys', 'get', 'getlist', 'has_key', 'items', 'iteritems', 'iterkeys', 'iterlists', 'iterlistvalues', 'itervalues', 'keys', 'lists', 'listvalues', 'pop', 'popitem', 'popitemlist', 'poplist', 'setdefault', 'setlist', 'setlistdefault', 'to_dict', 'update', 'values', 'viewitems', 'viewkeys', 'viewlists', 'viewlistvalues', 'viewvalues']
ipdb> request.files.getlist("images")
[<FileStorage: u'C7tMVgBWkAEqbbz (1).jpg' ('image/jpeg')>, <FileStorage: u'C7tMVgBWkAEqbbz.jpg-large' ('application/octet-stream')>, <FileStorage: u'DettePubliqueFrancaise_gauche_vs_droite.jpg' ('image/jpeg')>]
ipdb> request.files.getlist("images")[0]
<FileStorage: u'C7tMVgBWkAEqbbz (1).jpg' ('image/jpeg')>
ipdb> z = request.files.getlist("images")[0]
ipdb> dir(z)
['__bool__', '__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattr__', '__getattribute__', '__hash__', '__init__', '__iter__', '__module__', '__new__', '__nonzero__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_parse_content_type', 'close', 'content_length', 'content_type', 'filename', 'headers', 'mimetype', 'mimetype_params', 'name', 'save', 'stream']
ipdb> pdoc z.save
Class docstring:
    Save the file to a destination path or file object.  If the
    destination is a file object you have to close it yourself after the
    call.  The buffer size is the number of bytes held in memory during
    the copy process.  It defaults to 16KB.
    
    For secure file saving also have a look at :func:`secure_filename`.
    
    :param dst: a filename or open file object the uploaded file
                is saved to.
    :param buffer_size: the size of the buffer.  This works the same as
                        the `length` parameter of
                        :func:`shutil.copyfileobj`.
Call docstring:
    x.__call__(...) <==> x(...)
ipdb> request.form.keys()
['path']
ipdb> request.form["path"]
u'/build/'
ipdb> z.filename
u'C7tMVgBWkAEqbbz (1).jpg'
"""

@app.route("/")
def index():
    # this will run check that we can actually work here
    get_settings()

    return render_template("index.html")


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
