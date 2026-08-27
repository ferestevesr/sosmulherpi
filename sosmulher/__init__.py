import os

from dotenv import load_dotenv

from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt

from flask_login import (
    LoginManager,
    current_user
)

from flask_migrate import Migrate


load_dotenv()


app = Flask(__name__)


# =========================================================
# CONFIGURAÇÕES GERAIS
# =========================================================

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

migrate = Migrate(
    app,
    db
)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

login_manager.login_view = "auth.login"

login_manager.login_message = (
    "Faça login para acessar esta página."
)

login_manager.login_message_category = "info"


# =========================================================
# MODELS
# =========================================================

from sosmulher.models import *

from sosmulher.models.usuario import Usuario

from sosmulher.models.denuncia import Denuncia

from sosmulher.models.atualizacao_denuncia import (
    AtualizacaoDenuncia
)


# =========================================================
# CARREGAR USUÁRIO
# =========================================================

@login_manager.user_loader
def load_user(id_usuario):

    return db.session.get(
        Usuario,
        int(id_usuario)
    )


# =========================================================
# NOTIFICAÇÕES GLOBAIS
# =========================================================

@app.context_processor
def notificacoes_globais():

    # Usuário não está logado
    if not current_user.is_authenticated:

        return {
            "notificacoes_nao_lidas": 0
        }


    # Admin não precisa receber essas notificações
    if current_user.tipo == "admin":

        return {
            "notificacoes_nao_lidas": 0
        }


    # Conta apenas notificações das denúncias
    # pertencentes ao usuário logado
    total = (
        AtualizacaoDenuncia.query

        .join(
            Denuncia,
            AtualizacaoDenuncia.id_denuncia
            ==
            Denuncia.id_denuncia
        )

        .filter(
            Denuncia.id_usuario
            ==
            current_user.id_usuario,

            AtualizacaoDenuncia.lida.is_(False)
        )

        .count()
    )


    return {
        "notificacoes_nao_lidas": total
    }


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