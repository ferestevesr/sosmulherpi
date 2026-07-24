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
login_manager.login_view = "login"

from sosmulher.models import *

from sosmulher.models.usuario import Usuario

@login_manager.user_loader
def load_user(id_usuario):
    return Usuario.query.get(int(id_usuario))

from sosmulher.routes.home import home 
from sosmulher.routes.auth import auth

app.register_blueprint(home)
app.register_blueprint(auth)