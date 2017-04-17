import os
import yaml
import time

from PIL import Image

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

        return file.encode("Utf-8")

    if not os.path.exists(file):
        return ""

    return send_file(file, cache_timeout=0)


# for content not stored in built gallery
@app.route("/from_gallery/<path:path>")
def get_from_gallery_content(path):
    exif_to_rotation = {
        3: 180,
        6: 270,
        8: 90,
    }

    cache_dir = get_cache_dir()

    image_path = os.path.join(os.path.realpath(os.curdir), path)

    image_base_name, image_extension = ".".join(image_path.split(".")[:-1]), image_path.split(".")[-1]

    image_stats = os.stat(image_path)

    thumbnail_name = "%s-%s-%s.%s" % (image_base_name.replace("/", "_"), image_stats.st_size, int(image_stats.st_mtime), image_extension)

    thumbnail_path = os.path.join(cache_dir, "thumbnails", thumbnail_name)

    if not os.path.exists(thumbnail_path):
        try:
            image = Image.open(image_path)
        except Exception as e:
            print "Warning: while trying to read image '%s' using Pillow, exception '%s' occured, skipping" % (image_path, e)
            return send_file(image_path, cache_timeout=0)

        # in 2017, browser are still a pile of crap and don't honner exif tag
        # (except firefox and safari)
        # so, to avoid images oriented in the bad direction, we check if we need to
        # rotate them...

        # 274 if code for image rotation
        # read exif information, try to extract if I need to rotate the image
        # this will be done in css
        exif = getattr(image, "_getexif", lambda: None)()
        plop = exif.get(274) if exif else None
        rotation = exif_to_rotation.get(plop)
        print rotation, image_path

        if rotation:
            image = image.rotate(rotation, expand=True)

        image.thumbnail((300, 1000))
        image.save(thumbnail_path)

    return send_file(thumbnail_path, cache_timeout=0)


@app.route("/settings/build/")
def get_base_gallery_settings():
    return get_gallery_settings(".")


@app.route("/settings/build/<path:path>")
def get_gallery_settings(path):
    return open(os.path.join(path, "settings.yaml")).read()


@app.route("/images/build/<path:path>")
def get_gallery_images_list(path):
    settings = get_gallery_settings(path)

    images = [{
        "name": x.encode("Utf-8"),
        "used": x.encode("Utf-8") in settings,
    } for x in os.listdir(path) if x.lower().endswith((".gif", ".png", ".jpg", ".jpeg"))]

    images = sorted(images, key=lambda x: (x["used"], x["name"]))

    return render_template("images_zone.html", images=images, path=path)


def get_cache_dir():
    current_project_key = os.path.realpath(os.curdir).replace(".", "_")

    cache_dir = os.path.join(os.path.expanduser("~/.cache/prosopopee"), current_project_key)

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    if not os.path.exists(os.path.join(cache_dir, "thumbnails")):
        os.makedirs(os.path.join(cache_dir, "thumbnails"))

    return cache_dir


@app.route("/save_settings/build/", methods=['POST'])
def save_base_settings():
    return save_settings(".")


@app.route("/save_settings/build/<path:path>", methods=['POST'])
def save_settings(path):
    # TODO error in yaml

    assert request.form["settings"]
    newdata = request.form["settings"].encode('utf-8')
    open(os.path.join(path, "settings.yaml"), "w").write(newdata)

    build_everything()

    return "ok"


@app.route("/new_gallery/", methods=["POST"])
def new_gallery():
    if not os.path.exists(request.form["folder_name"]):
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
    path = request.form["path"].replace("/build/", "", 1)

    if not path:
        print "WARING: can't save image to root or to empty path '%s'" % request.form["path"]
        return "WARING: can't save image to root or to empty path '%s'" % request.form["path"]

    for f in request.files.getlist("images"):
        if not os.path.exists(os.path.join(path, f.filename)):
            filename = f.filename
        else:
            # avoid to overwrite existing file
            filename = ".".join(f.filename.split(".")[:-1] + ["-%s" % int(time.time())] + f.filename.split(".")[-1:])

        print "filename", "->", os.path.join(path, filename)
        f.save(os.path.join(path, filename))

    return "ok"


@app.route("/")
def index():
    # this will run check that we can actually work here
    get_settings()

    return render_template("index.html")


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
