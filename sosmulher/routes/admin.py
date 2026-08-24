from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from sosmulher import db
from sosmulher.models.usuario import Usuario
from sosmulher.models.denuncia import Denuncia
from sosmulher.models.pedido_sos import PedidoSOS
from sosmulher.models.pedido_sos_contato import PedidoSOSContato
from sosmulher.models.contato_emergencia import ContatoEmergencia


admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# ==========================
# DASHBOARD
# ==========================

@admin.route("/")
@login_required
def dashboard():

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    total_usuarios = Usuario.query.count()

    total_denuncias = Denuncia.query.count()

    denuncias_pendentes = Denuncia.query.filter_by(
        status="pendente"
    ).count()

    denuncias_andamento = Denuncia.query.filter_by(
        status="em_andamento"
    ).count()

    denuncias_finalizadas = Denuncia.query.filter_by(
        status="finalizado"
    ).count()

    denuncias_recentes = Denuncia.query.order_by(
        Denuncia.data.desc()
    ).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_usuarios=total_usuarios,
        total_denuncias=total_denuncias,
        denuncias_pendentes=denuncias_pendentes,
        denuncias_andamento=denuncias_andamento,
        denuncias_finalizadas=denuncias_finalizadas,
        denuncias_recentes=denuncias_recentes
    )


# ==========================
# USUÁRIOS
# ==========================

@admin.route("/usuarios")
@login_required
def usuarios():

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    usuarios = Usuario.query.all()

    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios
    )


# ==========================
# CHAMADOS SOS
# ==========================

@admin.route("/chamados")
@login_required
def chamados():

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    chamados = PedidoSOS.query.order_by(
        PedidoSOS.data_hora.desc()
    ).all()

    total_chamados = PedidoSOS.query.count()

    chamados_pendentes = PedidoSOS.query.filter_by(
        status="ativo"
    ).count()

    chamados_andamento = PedidoSOS.query.filter_by(
        status="em_andamento"
    ).count()

    chamados_finalizados = PedidoSOS.query.filter_by(
        status="finalizado"
    ).count()

    return render_template(
        "admin/chamados.html",
        chamados=chamados,
        total_chamados=total_chamados,
        chamados_pendentes=chamados_pendentes,
        chamados_andamento=chamados_andamento,
        chamados_finalizados=chamados_finalizados
    )


# ==========================
# VISUALIZAR CHAMADO SOS
# ==========================

@admin.route("/chamados/<int:id>")
@login_required
def visualizar_chamado(id):

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    chamado = PedidoSOS.query.get_or_404(id)

    contatos = PedidoSOSContato.query.filter_by(
        id_sos=chamado.id_sos
    ).all()

    return render_template(
        "admin/visualizar_chamado.html",
        chamado=chamado,
        contatos=contatos
    )


# ==========================
# ACIONAR CONTATOS DE EMERGÊNCIA
# ==========================

@admin.route("/chamados/<int:id>/acionar-contatos", methods=["POST"])
@login_required
def acionar_contatos(id):

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para realizar esta ação.",
            "danger"
        )
        return redirect(url_for("home.index"))

    chamado = PedidoSOS.query.get_or_404(id)

    # Impede que um chamado já finalizado seja acionado novamente
    if chamado.status == "finalizado":
        flash(
            "Os contatos de emergência deste chamado já foram acionados.",
            "info"
        )
        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

    # Só permite o acionamento quando o chamado
    # estiver aguardando atendimento
    if chamado.status != "em_andamento":
        flash(
            "Este chamado não está disponível para acionamento.",
            "warning"
        )
        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

    # Verifica se existem contatos vinculados ao chamado
    contatos = PedidoSOSContato.query.filter_by(
        id_sos=chamado.id_sos
    ).all()

    if not contatos:
        flash(
            "Este chamado não possui contatos de emergência cadastrados.",
            "warning"
        )
        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

    # Aqui registramos que os contatos foram acionados.
    #
    # Como o modelo atual de PedidoSOSContato ainda não possui
    # um campo específico de status/data de acionamento,
    # o próprio status do chamado representa esse momento.
    chamado.status = "finalizado"

    db.session.commit()

    flash(
        "Contatos de emergência acionados com sucesso. "
        "O chamado foi finalizado.",
        "success"
    )

    return redirect(
        url_for(
            "admin.visualizar_chamado",
            id=chamado.id_sos
        )
    )


# ==========================
# ATENDIMENTO
# ==========================

@admin.route("/atendimento")
@login_required
def atendimento():

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    atendimentos = Denuncia.query.all()

    atendimentos_pendentes = Denuncia.query.filter_by(
        status="pendente"
    ).count()

    atendimentos_andamento = Denuncia.query.filter_by(
        status="em_andamento"
    ).count()

    atendimentos_finalizados = Denuncia.query.filter_by(
        status="finalizado"
    ).count()

    total_atendimentos = Denuncia.query.count()

    return render_template(
        "admin/atendimento.html",
        atendimentos_andamento=atendimentos_andamento,
        atendimentos_pendentes=atendimentos_pendentes,
        atendimentos_finalizados=atendimentos_finalizados,
        total_atendimentos=total_atendimentos,
        atendimentos=atendimentos
    )


# ==========================
# VISUALIZAR ATENDIMENTO
# ==========================

@admin.route("/atendimento/<int:id>")
@login_required
def visualizar_atendimento(id):

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    atendimento = Denuncia.query.get_or_404(id)

    return render_template(
        "admin/visualizar_atendimento.html",
        atendimento=atendimento
    )


# ==========================
# RELATÓRIOS
# ==========================

@admin.route("/relatorios")
@login_required
def relatorios():

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    # ==========================
    # CHAMADOS SOS
    # ==========================

    total_chamados = PedidoSOS.query.count()

    chamados_ativos = PedidoSOS.query.filter_by(
        status="ativo"
    ).count()

    chamados_andamento = PedidoSOS.query.filter_by(
        status="em_andamento"
    ).count()

    chamados_finalizados = PedidoSOS.query.filter_by(
        status="finalizado"
    ).count()

    # ==========================
    # DENÚNCIAS
    # ==========================

    total_denuncias = Denuncia.query.count()

    denuncias_pendentes = Denuncia.query.filter_by(
        status="pendente"
    ).count()

    denuncias_andamento = Denuncia.query.filter_by(
        status="em_andamento"
    ).count()

    denuncias_finalizadas = Denuncia.query.filter_by(
        status="finalizado"
    ).count()

    # ==========================
    # USUÁRIOS
    # ==========================

    total_usuarios = Usuario.query.count()

    # ==========================
    # TOTAIS GERAIS
    # ==========================

    total_andamento = (
        chamados_andamento +
        denuncias_andamento
    )

    total_finalizados = (
        chamados_finalizados +
        denuncias_finalizadas
    )

    ocorrencias_totais = (
        total_chamados +
        total_denuncias
    )

    # ==========================
    # ENVIAR DADOS PARA O HTML
    # ==========================

    return render_template(
        "admin/relatorios.html",

        total_chamados=total_chamados,

        chamados_ativos=chamados_ativos,

        chamados_andamento=chamados_andamento,

        chamados_finalizados=chamados_finalizados,

        total_denuncias=total_denuncias,

        denuncias_pendentes=denuncias_pendentes,

        denuncias_andamento=denuncias_andamento,

        denuncias_finalizadas=denuncias_finalizadas,

        total_usuarios=total_usuarios,

        total_andamento=total_andamento,

        total_finalizados=total_finalizados,

        ocorrencias_totais=ocorrencias_totais
    )


# ==========================
# CONFIGURAÇÕES
# ==========================

@admin.route("/configuracoes")
@login_required
def configuracoes():

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    return render_template("admin/configuracoes.html")