from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate


app = Flask(__name__)

app.config["SECRET_KEY"] = "sua_chave_secreta"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///database.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"


from sosmulher.models import *
from sosmulher.models.usuario import Usuario


@login_manager.user_loader
def load_user(id_usuario):
    return Usuario.query.get(int(id_usuario))


# ==========================
# ROTAS / BLUEPRINTS
# ==========================

from sosmulher.routes.home import home
from sosmulher.routes.auth import auth
from sosmulher.routes.contato import contato
from sosmulher.routes.denuncia import denuncia
from sosmulher.routes.perfil import perfil
from sosmulher.routes.admin import admin
from sosmulher.routes.sos import sos


# ==========================
# REGISTRAR BLUEPRINTS
# ==========================

app.register_blueprint(home)
app.register_blueprint(auth)
app.register_blueprint(contato)
app.register_blueprint(denuncia)
app.register_blueprint(perfil)
app.register_blueprint(admin)
app.register_blueprint(sos)