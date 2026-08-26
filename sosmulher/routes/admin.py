from flask import ( Blueprint, render_template, redirect, url_for, flash, request )
from datetime import datetime
from flask_login import login_required, current_user

from sosmulher import db
from sosmulher.models.usuario import Usuario
from sosmulher.models.denuncia import Denuncia
from sosmulher.models.pedido_sos import PedidoSOS
from sosmulher.models.pedido_sos_contato import PedidoSOSContato



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

@admin.route(
    "/chamados/<int:id>/acionar-contatos",
    methods=["POST"]
)
@login_required
def acionar_contatos(id):

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para realizar esta ação.",
            "danger"
        )
        return redirect(url_for("home.index"))

    chamado = PedidoSOS.query.get_or_404(id)

    # Chamado finalizado não pode ser acionado novamente
    if chamado.status == "finalizado":

        flash(
            "Este chamado já foi finalizado.",
            "info"
        )

        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

    # Chamado em andamento já teve os contatos acionados
    if chamado.status == "em_andamento":

        flash(
            "Os contatos deste chamado já foram acionados.",
            "info"
        )

        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

    # Apenas chamado ATIVO pode iniciar atendimento
    if chamado.status != "ativo":

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

    # Verifica contatos vinculados
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

    # Contatos acionados -> atendimento começa
    chamado.status = "em_andamento"

    db.session.commit()

    flash(
        "Contatos de emergência acionados. "
        "O chamado agora está em andamento.",
        "success"
    )

    return redirect(
        url_for(
            "admin.visualizar_chamado",
            id=chamado.id_sos
        )
    )
# ==========================
# ENCAMINHAR CHAMADO
# ==========================

@admin.route(
    "/chamados/<int:id>/encaminhar",
    methods=["POST"]
)
@login_required
def encaminhar_chamado(id):

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para realizar esta ação.",
            "danger"
        )
        return redirect(url_for("home.index"))

    chamado = PedidoSOS.query.get_or_404(id)

    # Só chamados ativos podem ser encaminhados
    if chamado.status != "ativo":

        flash(
            "Este chamado não está disponível para encaminhamento.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

    # Verifica se existem contatos pessoais
    contatos = PedidoSOSContato.query.filter_by(
        id_sos=chamado.id_sos
    ).all()

    # Se existem contatos, usa o fluxo normal
    if contatos:

        flash(
            "Este chamado possui contatos de emergência. "
            "Utilize primeiro o acionamento dos contatos cadastrados.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

    tipo = request.form.get(
        "tipo_encaminhamento"
    )

    encaminhamentos_validos = {
        "190": "Emergência policial",
        "180": "Central de Atendimento à Mulher",
        "192": "SAMU"
    }

    if tipo not in encaminhamentos_validos:

        flash(
            "Tipo de encaminhamento inválido.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

    # Registra o encaminhamento
    chamado.tipo_encaminhamento = tipo

    chamado.data_encaminhamento = datetime.now()

    chamado.observacao_encaminhamento = (
        encaminhamentos_validos[tipo]
    )

    # Atendimento passa para em andamento
    chamado.status = "em_andamento"

    db.session.commit()

    flash(
        f"Encaminhamento para "
        f"{encaminhamentos_validos[tipo]} "
        f"registrado com sucesso. "
        f"O chamado agora está em andamento.",
        "success"
    )

    return redirect(
        url_for(
            "admin.visualizar_chamado",
            id=chamado.id_sos
        )
    )
# ==========================
# FINALIZAR CHAMADO SOS
# ==========================

@admin.route(
    "/chamados/<int:id>/finalizar",
    methods=["POST"]
)
@login_required
def finalizar_chamado(id):

    if current_user.tipo != "admin":

        flash(
            "Você não tem permissão para realizar esta ação.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    chamado = PedidoSOS.query.get_or_404(id)

    # Já finalizado
    if chamado.status == "finalizado":

        flash(
            "Este chamado já foi finalizado.",
            "info"
        )

        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

    # Só pode finalizar depois de iniciar atendimento
    if chamado.status != "em_andamento":

        flash(
            "Este chamado precisa estar em andamento antes de ser finalizado.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

    chamado.status = "finalizado"

    db.session.commit()

    flash(
        "Chamado finalizado com sucesso.",
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
# INICIAR ATENDIMENTO
# ==========================

@admin.route(
    "/atendimento/<int:id>/iniciar",
    methods=["POST"]
)
@login_required
def iniciar_atendimento(id):

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para realizar esta ação.",
            "danger"
        )
        return redirect(url_for("home.index"))

    denuncia = Denuncia.query.get_or_404(id)

    # Já finalizada
    if denuncia.status == "finalizado":

        flash(
            "Esta denúncia já foi finalizada.",
            "info"
        )

        return redirect(
            url_for(
                "admin.visualizar_atendimento",
                id=denuncia.id_denuncia
            )
        )

    # Já está em atendimento
    if denuncia.status == "em_andamento":

        flash(
            "Esta denúncia já está em atendimento.",
            "info"
        )

        return redirect(
            url_for(
                "admin.visualizar_atendimento",
                id=denuncia.id_denuncia
            )
        )

    # Apenas pendente pode iniciar atendimento
    if denuncia.status != "pendente":

        flash(
            "Esta denúncia não está disponível para atendimento.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.visualizar_atendimento",
                id=denuncia.id_denuncia
            )
        )

    denuncia.status = "em_andamento"

    db.session.commit()

    flash(
        "Atendimento iniciado com sucesso.",
        "success"
    )

    return redirect(
        url_for(
            "admin.visualizar_atendimento",
            id=denuncia.id_denuncia
        )
    )


# ==========================
# FINALIZAR ATENDIMENTO
# ==========================

@admin.route(
    "/atendimento/<int:id>/finalizar",
    methods=["POST"]
)
@login_required
def finalizar_atendimento(id):

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para realizar esta ação.",
            "danger"
        )
        return redirect(url_for("home.index"))

    denuncia = Denuncia.query.get_or_404(id)

    # Já finalizada
    if denuncia.status == "finalizado":

        flash(
            "Esta denúncia já foi finalizada.",
            "info"
        )

        return redirect(
            url_for(
                "admin.visualizar_atendimento",
                id=denuncia.id_denuncia
            )
        )

    # Precisa estar em andamento
    if denuncia.status != "em_andamento":

        flash(
            "O atendimento precisa ser iniciado antes de ser finalizado.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.visualizar_atendimento",
                id=denuncia.id_denuncia
            )
        )

    denuncia.status = "finalizado"

    db.session.commit()

    flash(
        "Atendimento finalizado com sucesso.",
        "success"
    )

    return redirect(
        url_for(
            "admin.visualizar_atendimento",
            id=denuncia.id_denuncia
        )
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