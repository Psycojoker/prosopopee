import os
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


@app.route("/")
def index():
    # this will run check that we can actually work here
    get_settings()

    return render_template("index.html")


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
