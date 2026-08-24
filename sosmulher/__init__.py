from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
import os


app = Flask(__name__)

app.config["SECRET_KEY"] = "sua_chave_secreta"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///database.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# =========================================================
# E-MAIL
# =========================================================

app.config["MAIL_SERVER"] = "smtp.gmail.com"

app.config["MAIL_PORT"] = 587

app.config["MAIL_USERNAME"] = os.getenv(
    "MAIL_USERNAME"
)

app.config["MAIL_PASSWORD"] = os.getenv(
    "MAIL_PASSWORD"
)

app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
    "MAIL_USERNAME"
)


# =========================================================
# EXTENSÕES
# =========================================================

db = SQLAlchemy(app)

migrate = Migrate(app, db)

bcrypt = Bcrypt(app)


login_manager = LoginManager(app)

login_manager.login_view = "auth.login"


# =========================================================
# MODELS
# =========================================================

from sosmulher.models import *
from sosmulher.models.usuario import Usuario


@login_manager.user_loader
def load_user(id_usuario):

    return Usuario.query.get(
        int(id_usuario)
    )


# =========================================================
# BLUEPRINTS
# =========================================================

from sosmulher.routes.home import home
from sosmulher.routes.auth import auth
from sosmulher.routes.contato import contato
from sosmulher.routes.denuncia import denuncia
from sosmulher.routes.perfil import perfil
from sosmulher.routes.admin import admin


# =========================================================
# REGISTRAR BLUEPRINTS
# =========================================================

app.register_blueprint(home)

app.register_blueprint(auth)

app.register_blueprint(contato)

app.register_blueprint(denuncia)

app.register_blueprint(perfil)

app.register_blueprint(admin)