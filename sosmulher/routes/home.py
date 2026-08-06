from flask import render_template
from sosmulher import app
from flask import Blueprint

home = Blueprint("home", __name__)


@home.route("/")
def index():
    return render_template("index.html")


@home.route("/apoio")
def apoio():
    return render_template("apoio.html")


@home.route("/anonimo")
def anonimo():
    return render_template("anonimo.html")


@home.route("/denuncias")
def denuncias():
    return render_template("denuncias.html")

@home.route("/sos")
def sos():
    return render_template("sos.html")