
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)

from flask_login import (
    login_required,
    current_user
)

from sosmulher import db

from sosmulher.forms import DenunciaForm

from sosmulher.models.denuncia import Denuncia

from sosmulher.models.atualizacao_denuncia import (
    AtualizacaoDenuncia
)

from sosmulher.services.denuncia_service import (
    criar_denuncia,
    listar_denuncias_usuario
)

from sosmulher.services.upload_service import (
    salvar_arquivo
)

denuncia = Blueprint(
    "denuncia",
    __name__
)


@denuncia.route(
    "/denuncia",
    methods=["GET", "POST"]
)
@login_required
def denunciar():

    form = DenunciaForm()

    if request.method == "POST":

        if form.validate():

            denuncia_criada = criar_denuncia(
                form,
                current_user
            )

            if form.arquivo.data:
                salvar_arquivo(
                    form.arquivo.data,
                    denuncia_criada.id_denuncia
                )

            flash(
                "Denúncia enviada com sucesso!",
                "success"
            )

            return redirect(
                url_for("home.index")
            )

    return render_template(
        "denuncia.html",
        form=form
    )


@denuncia.route("/denuncias")
@login_required
def denuncias():

    denuncias = listar_denuncias_usuario(
        current_user.id_usuario
    )

    return render_template(
        "denuncias.html",
        denuncias=denuncias
    )

# =========================================================
# NOTIFICAÇÕES DO USUÁRIO
# =========================================================

@denuncia.route("/notificacoes")
@login_required
def notificacoes():

    atualizacoes = (
        AtualizacaoDenuncia.query
        .join(
            Denuncia,
            AtualizacaoDenuncia.id_denuncia
            == Denuncia.id_denuncia
        )
        .filter(
            Denuncia.id_usuario
            == current_user.id_usuario
        )
        .order_by(
            AtualizacaoDenuncia.data.desc()
        )
        .all()
    )

    for atualizacao in atualizacoes:

        if not atualizacao.lida:
            atualizacao.lida = True

    db.session.commit()

    return render_template(
        "notificacoes.html",
        atualizacoes=atualizacoes
    )