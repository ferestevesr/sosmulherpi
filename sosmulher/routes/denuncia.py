
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    current_app,
    send_from_directory
)

from flask_login import (
    login_required,
    current_user
)

from sosmulher import db

from sosmulher.forms import DenunciaForm

from sosmulher.models.denuncia import Denuncia
from sosmulher.models.arquivo import Arquivo

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
from sosmulher.models.pedido_sos import PedidoSOS
from sosmulher.models.atualizacao_sos import AtualizacaoSOS


@denuncia.route("/arquivos/<int:id_arquivo>")
@login_required
def arquivo(id_arquivo):
    """Entrega evidências apenas à autora da denúncia ou a um administrador."""
    anexo = Arquivo.query.get_or_404(id_arquivo)

    if (
        current_user.tipo != "admin"
        and anexo.denuncia.id_usuario != current_user.id_usuario
    ):
        abort(403)

    pasta_upload = current_app.instance_path + "/uploads"
    return send_from_directory(pasta_upload, anexo.nome_arquivo)


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


@denuncia.route("/denuncias/<int:id_denuncia>")
@login_required
def detalhes_denuncia(id_denuncia):
    """Exibe à usuária somente os detalhes e o histórico do próprio caso."""
    denuncia_usuario = Denuncia.query.filter_by(
        id_denuncia=id_denuncia,
        id_usuario=current_user.id_usuario
    ).first_or_404()
    atualizacoes = (
        AtualizacaoDenuncia.query
        .filter_by(id_denuncia=denuncia_usuario.id_denuncia)
        .order_by(AtualizacaoDenuncia.data.asc())
        .all()
    )
    return render_template(
        "detalhes_denuncia.html",
        denuncia=denuncia_usuario,
        atualizacoes=atualizacoes
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

    atualizacoes_sos = (
        AtualizacaoSOS.query
        .join(PedidoSOS, AtualizacaoSOS.id_sos == PedidoSOS.id_sos)
        .filter(PedidoSOS.id_usuario == current_user.id_usuario)
        .order_by(AtualizacaoSOS.data.desc())
        .all()
    )

    for atualizacao in atualizacoes_sos:
        atualizacao.lida = True

    db.session.commit()

    return render_template(
        "notificacoes.html",
        atualizacoes=atualizacoes,
        atualizacoes_sos=atualizacoes_sos
    )
