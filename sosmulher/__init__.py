import os
from datetime import timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    current_user,
    logout_user
)
from flask_migrate import Migrate


load_dotenv()


# =========================================================
# APP
# =========================================================

app = Flask(__name__)


# =========================================================
# CONFIGURAÇÕES GERAIS
# =========================================================

# Em produção, defina SECRET_KEY no ambiente. O valor de reserva evita que
# sessões possam ser forjadas quando a aplicação é executada localmente.
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or os.urandom(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
)

# Limite único para anexos de denúncias; evita consumo excessivo de disco.
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

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
#
# IMPORTANTE:
# Só importar os models DEPOIS que o db foi criado.
# =========================================================

from sosmulher.models.usuario import Usuario

from sosmulher.models.denuncia import Denuncia

from sosmulher.models.atualizacao_denuncia import (
    AtualizacaoDenuncia
)
from sosmulher.models.pedido_sos import PedidoSOS
from sosmulher.models.atualizacao_sos import AtualizacaoSOS


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

    notificacoes_nao_lidas = 0

    if (
        current_user.is_authenticated
        and current_user.tipo != "admin"
    ):

        notificacoes_nao_lidas = (
            AtualizacaoDenuncia.query
            .join(
                Denuncia,
                AtualizacaoDenuncia.id_denuncia
                == Denuncia.id_denuncia
            )
            .filter(
                Denuncia.id_usuario
                == current_user.id_usuario,
                AtualizacaoDenuncia.lida.is_(False)
            )
            .count()
        )

        notificacoes_nao_lidas += (
            AtualizacaoSOS.query
            .join(PedidoSOS, AtualizacaoSOS.id_sos == PedidoSOS.id_sos)
            .filter(
                PedidoSOS.id_usuario == current_user.id_usuario,
                AtualizacaoSOS.lida.is_(False)
            )
            .count()
        )

    return {
        "notificacoes_nao_lidas":
        notificacoes_nao_lidas
    }

# =========================================================
# HORÁRIO DE BRASÍLIA
# =========================================================

@app.template_filter("horario_brasilia")
def horario_brasilia(data):

    if data is None:
        return ""

    # Datas do banco estão sem informação de fuso.
    # Consideramos que foram armazenadas em UTC.
    if data.tzinfo is None:
        data = data.replace(
            tzinfo=timezone.utc
        )

    brasilia = ZoneInfo(
        "America/Sao_Paulo"
    )

    data_brasilia = data.astimezone(
        brasilia
    )

    return data_brasilia.strftime(
        "%d/%m/%Y às %H:%M"
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


@app.before_request
def encerrar_sessao_de_conta_indisponivel():
    """Impede que uma sessão antiga mantenha uma conta bloqueada ativa."""
    if (
        current_user.is_authenticated
        and current_user.status_conta != "ativa"
        and request.endpoint != "static"
    ):
        logout_user()
        flash(
            "Esta conta não está disponível para acesso. Procure a administração.",
            "warning"
        )
        return redirect(url_for("auth.login"))


@app.errorhandler(413)
def arquivo_muito_grande(erro):
    """Retorna uma mensagem útil quando um anexo ultrapassa o limite."""
    if request.path.startswith("/api/"):
        return jsonify({
            "sucesso": False,
            "mensagem": "O anexo deve ter no máximo 10 MB."
        }), 413

    flash("O anexo deve ter no máximo 10 MB.", "danger")
    return redirect(url_for("denuncia.denunciar"))
