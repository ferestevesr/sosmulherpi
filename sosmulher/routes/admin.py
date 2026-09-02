from flask import (
    Blueprint,
    current_app,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    send_file
)

from datetime import datetime, timedelta
from io import StringIO, BytesIO
import csv

from flask_login import (
    login_required,
    current_user
)

from sosmulher import db

from sosmulher.models.usuario import Usuario
from sosmulher.models.denuncia import Denuncia
from sosmulher.models.pedido_sos import PedidoSOS
from sosmulher.models.pedido_sos_contato import PedidoSOSContato

from sosmulher.models.atualizacao_denuncia import (
    AtualizacaoDenuncia
)

from sosmulher.models.atualizacao_sos import (
    AtualizacaoSOS
)


admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


@admin.before_request
def exigir_admin():
    """Protege integralmente o painel, inclusive novas rotas adicionadas."""
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    if current_user.tipo != "admin":
        flash("Você não tem permissão para acessar esta página.", "danger")
        return redirect(url_for("home.index"))


@admin.after_request
def registrar_acao_administrativa(resposta):
    """Deixa rastros operacionais de ações que alteram o estado do painel."""
    if request.method != "GET" and resposta.status_code < 400:
        current_app.logger.info(
            "admin_action admin_id=%s method=%s path=%s status=%s",
            current_user.id_usuario,
            request.method,
            request.path,
            resposta.status_code
        )
    return resposta


# =========================================================
# VERIFICAR ADMIN
# =========================================================

def usuario_e_admin():

    return (
        current_user.is_authenticated
        and current_user.tipo == "admin"
    )


# =========================================================
# DASHBOARD
# =========================================================

@admin.route("/")
@login_required
def dashboard():

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

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

    # Série simples para o gráfico dos últimos sete dias, sem depender
    # de serviços externos ou de uma rotina de agregação separada.
    hoje = datetime.now().date()
    grafico_dias = []
    for deslocamento in range(6, -1, -1):
        dia = hoje - timedelta(days=deslocamento)
        inicio = datetime.combine(dia, datetime.min.time())
        fim = inicio + timedelta(days=1)
        quantidade = (
            Denuncia.query.filter(Denuncia.data >= inicio, Denuncia.data < fim).count()
            + PedidoSOS.query.filter(PedidoSOS.data_hora >= inicio, PedidoSOS.data_hora < fim).count()
        )
        grafico_dias.append({
            "rotulo": dia.strftime("%d/%m"),
            "quantidade": quantidade
        })

    maximo_grafico = max((item["quantidade"] for item in grafico_dias), default=1) or 1

    return render_template(
        "admin/dashboard.html",
        total_usuarios=total_usuarios,
        total_denuncias=total_denuncias,
        denuncias_pendentes=denuncias_pendentes,
        denuncias_andamento=denuncias_andamento,
        denuncias_finalizadas=denuncias_finalizadas,
        denuncias_recentes=denuncias_recentes,
        grafico_dias=grafico_dias,
        maximo_grafico=maximo_grafico
    )


# =========================================================
# USUÁRIOS
# =========================================================

@admin.route("/usuarios")
@login_required
def usuarios():

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    busca = request.args.get("busca", "").strip()
    consulta = Usuario.query
    if busca:
        termo = f"%{busca}%"
        filtros = [Usuario.nome.ilike(termo), Usuario.email.ilike(termo)]
        if busca.isdigit():
            filtros.append(Usuario.id_usuario == int(busca))
        from sqlalchemy import or_
        consulta = consulta.filter(or_(*filtros))

    usuarios = consulta.order_by(Usuario.nome.asc()).all()

    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios,
        busca=busca
    )


# =========================================================
# CHAMADOS SOS
# =========================================================

@admin.route("/chamados")
@login_required
def chamados():

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    status = request.args.get("status", "").strip()
    busca = request.args.get("busca", "").strip()
    pagina = request.args.get("pagina", 1, type=int)

    consulta = PedidoSOS.query

    if status in {"ativo", "em_andamento", "finalizado", "cancelado"}:
        consulta = consulta.filter(PedidoSOS.status == status)

    if busca.isdigit():
        consulta = consulta.filter(PedidoSOS.id_sos == int(busca))

    chamados_paginados = consulta.order_by(
        PedidoSOS.data_hora.desc()
    ).paginate(page=pagina, per_page=20, error_out=False)

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
        chamados=chamados_paginados.items,
        chamados_paginados=chamados_paginados,
        filtro_status=status,
        busca=busca,
        total_chamados=total_chamados,
        chamados_pendentes=chamados_pendentes,
        chamados_andamento=chamados_andamento,
        chamados_finalizados=chamados_finalizados
    )


# =========================================================
# VISUALIZAR CHAMADO SOS
# =========================================================

@admin.route("/chamados/<int:id>")
@login_required
def visualizar_chamado(id):

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    chamado = PedidoSOS.query.get_or_404(id)

    contatos = PedidoSOSContato.query.filter_by(
        id_sos=chamado.id_sos
    ).all()

    return render_template(
        "admin/visualizar_chamado.html",
        chamado=chamado,
        contatos=contatos
    )


# =========================================================
# ACIONAR CONTATOS DE EMERGÊNCIA
# =========================================================

@admin.route(
    "/chamados/<int:id>/acionar-contatos",
    methods=["POST"]
)
@login_required
def acionar_contatos(id):

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para realizar esta ação.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    chamado = PedidoSOS.query.get_or_404(id)

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

    if chamado.status == "em_andamento":

        flash(
            "Este chamado já está em andamento.",
            "info"
        )

        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

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

    contatos = PedidoSOSContato.query.filter_by(
        id_sos=chamado.id_sos
    ).all()

    # =====================================================
    # SEM CONTATOS
    # =====================================================

    if not contatos:

        flash(
            "Este chamado não possui contatos de emergência. "
            "Utilize o encaminhamento para 180, 190 ou 192.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

    # =====================================================
    # COM CONTATOS
    # =====================================================

    status_anterior = chamado.status

    chamado.status = "em_andamento"

    atualizacao = AtualizacaoSOS(
        id_sos=chamado.id_sos,
        id_admin=current_user.id_usuario,
        mensagem=(
            "Seu pedido SOS está sendo atendido. "
            "Os contatos de emergência cadastrados "
            "foram acionados. "
            f"Protocolo SOS #{chamado.id_sos:06d}."
        ),
        status_anterior=status_anterior,
        status_novo="em_andamento",
        lida=False
    )

    db.session.add(atualizacao)

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


# =========================================================
# ENCAMINHAR CHAMADO
# =========================================================

@admin.route(
    "/chamados/<int:id>/encaminhar",
    methods=["POST"]
)
@login_required
def encaminhar_chamado(id):

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para realizar esta ação.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    chamado = PedidoSOS.query.get_or_404(id)

    # =====================================================
    # VERIFICA STATUS
    # =====================================================

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

    if chamado.status == "em_andamento":

        flash(
            "Este chamado já está em andamento.",
            "info"
        )

        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

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

    # =====================================================
    # VERIFICA CONTATOS
    # =====================================================

    contatos = PedidoSOSContato.query.filter_by(
        id_sos=chamado.id_sos
    ).all()

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

    # =====================================================
    # TIPO DE ENCAMINHAMENTO
    # =====================================================

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

    # =====================================================
    # ALTERAR CHAMADO
    # =====================================================

    status_anterior = chamado.status

    chamado.tipo_encaminhamento = tipo

    chamado.data_encaminhamento = datetime.now()

    chamado.observacao_encaminhamento = (
        encaminhamentos_validos[tipo]
    )

    chamado.status = "em_andamento"

    # =====================================================
    # NOTIFICAÇÃO DO USUÁRIO
    # =====================================================

    atualizacao = AtualizacaoSOS(
        id_sos=chamado.id_sos,
        id_admin=current_user.id_usuario,
        mensagem=(
            f"Seu pedido SOS foi encaminhado para "
            f"{encaminhamentos_validos[tipo]} "
            f"({tipo}). "
            f"Protocolo SOS #{chamado.id_sos:06d}."
        ),
        status_anterior=status_anterior,
        status_novo="em_andamento",
        lida=False
    )

    db.session.add(atualizacao)

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


# =========================================================
# FINALIZAR CHAMADO SOS
# =========================================================

@admin.route(
    "/chamados/<int:id>/finalizar",
    methods=["POST"]
)
@login_required
def finalizar_chamado(id):

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para realizar esta ação.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    chamado = PedidoSOS.query.get_or_404(id)

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

    if chamado.status != "em_andamento":

        flash(
            "Este chamado precisa estar em andamento "
            "antes de ser finalizado.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.visualizar_chamado",
                id=chamado.id_sos
            )
        )

    # =====================================================
    # FINALIZA
    # =====================================================

    status_anterior = chamado.status

    chamado.status = "finalizado"

    # =====================================================
    # NOTIFICAÇÃO
    # =====================================================

    atualizacao = AtualizacaoSOS(
        id_sos=chamado.id_sos,
        id_admin=current_user.id_usuario,
        mensagem=(
            "O atendimento do seu pedido SOS "
            "foi finalizado. "
            f"Protocolo SOS #{chamado.id_sos:06d}."
        ),
        status_anterior=status_anterior,
        status_novo="finalizado",
        lida=False
    )

    db.session.add(atualizacao)

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


# =========================================================
# ATENDIMENTOS / DENÚNCIAS
# =========================================================

@admin.route("/atendimento")
@login_required
def atendimento():

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    status = request.args.get("status", "").strip()
    busca = request.args.get("busca", "").strip()
    pagina = request.args.get("pagina", 1, type=int)

    risco = request.args.get("risco", "").strip()
    consulta = Denuncia.query

    if status in {"pendente", "em_andamento", "finalizado", "cancelado"}:
        consulta = consulta.filter(Denuncia.status == status)

    if risco in {"baixo", "medio", "alto", "emergencia"}:
        consulta = consulta.filter(Denuncia.nivel_risco == risco)

    if busca.isdigit():
        consulta = consulta.filter(Denuncia.id_denuncia == int(busca))
    elif busca:
        consulta = consulta.filter(Denuncia.titulo.ilike(f"%{busca}%"))

    atendimentos_paginados = consulta.order_by(
        Denuncia.data.desc()
    ).paginate(page=pagina, per_page=20, error_out=False)

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
        atendimentos=atendimentos_paginados.items,
        atendimentos_paginados=atendimentos_paginados,
        filtro_status=status,
        filtro_risco=risco,
        busca=busca
    )


# =========================================================
# VISUALIZAR ATENDIMENTO
# =========================================================

@admin.route("/atendimento/<int:id>")
@login_required
def visualizar_atendimento(id):

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    atendimento = Denuncia.query.get_or_404(id)

    atualizacoes = (
        AtualizacaoDenuncia.query
        .filter_by(
            id_denuncia=atendimento.id_denuncia
        )
        .order_by(
            AtualizacaoDenuncia.data.desc()
        )
        .all()
    )

    return render_template(
        "admin/visualizar_atendimento.html",
        atendimento=atendimento,
        atualizacoes=atualizacoes
    )


# =========================================================
# INICIAR ATENDIMENTO
# =========================================================

@admin.route(
    "/atendimento/<int:id>/iniciar",
    methods=["POST"]
)
@login_required
def iniciar_atendimento(id):

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para realizar esta ação.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    denuncia = Denuncia.query.get_or_404(id)

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

    # =====================================================
    # ALTERAR STATUS
    # =====================================================

    status_anterior = denuncia.status

    mensagem = request.form.get(
        "mensagem",
        ""
    ).strip()

    denuncia.status = "em_andamento"

    # =====================================================
    # MENSAGEM PADRÃO
    # =====================================================

    if not mensagem:

        mensagem = (
            f"Atendimento iniciado. "
            f"Protocolo #{denuncia.id_denuncia:06d}."
        )

    # =====================================================
    # NOTIFICAÇÃO
    # =====================================================

    atualizacao = AtualizacaoDenuncia(
        id_denuncia=denuncia.id_denuncia,
        id_admin=current_user.id_usuario,
        mensagem=mensagem,
        status_anterior=status_anterior,
        status_novo="em_andamento",
        lida=False
    )

    db.session.add(atualizacao)

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


# =========================================================
# ADICIONAR ATUALIZAÇÃO AO ATENDIMENTO
# =========================================================

@admin.route(
    "/atendimento/<int:id>/atualizacao",
    methods=["POST"]
)
@login_required
def adicionar_atualizacao(id):

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para realizar esta ação.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    denuncia = Denuncia.query.get_or_404(id)

    if denuncia.status == "finalizado":

        flash(
            "Não é possível adicionar atualizações "
            "em uma denúncia finalizada.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.visualizar_atendimento",
                id=denuncia.id_denuncia
            )
        )

    mensagem = request.form.get(
        "mensagem",
        ""
    ).strip()

    if not mensagem:

        flash(
            "Digite uma mensagem para o usuário.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.visualizar_atendimento",
                id=denuncia.id_denuncia
            )
        )

    atualizacao = AtualizacaoDenuncia(
        id_denuncia=denuncia.id_denuncia,
        id_admin=current_user.id_usuario,
        mensagem=mensagem,
        status_anterior=denuncia.status,
        status_novo=denuncia.status,
        lida=False
    )

    db.session.add(atualizacao)

    db.session.commit()

    flash(
        "Atualização enviada para o usuário.",
        "success"
    )

    return redirect(
        url_for(
            "admin.visualizar_atendimento",
            id=denuncia.id_denuncia
        )
    )


# =========================================================
# FINALIZAR ATENDIMENTO
# =========================================================

@admin.route(
    "/atendimento/<int:id>/finalizar",
    methods=["POST"]
)
@login_required
def finalizar_atendimento(id):

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para realizar esta ação.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    denuncia = Denuncia.query.get_or_404(id)

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

    if denuncia.status != "em_andamento":

        flash(
            "O atendimento precisa ser iniciado "
            "antes de ser finalizado.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.visualizar_atendimento",
                id=denuncia.id_denuncia
            )
        )

    # =====================================================
    # ALTERAR STATUS
    # =====================================================

    status_anterior = denuncia.status

    mensagem = request.form.get(
        "mensagem",
        ""
    ).strip()

    denuncia.status = "finalizado"

    # =====================================================
    # MENSAGEM PADRÃO
    # =====================================================

    if not mensagem:

        mensagem = (
            "O atendimento desta denúncia foi finalizado."
        )

    # =====================================================
    # NOTIFICAÇÃO
    # =====================================================

    atualizacao = AtualizacaoDenuncia(
        id_denuncia=denuncia.id_denuncia,
        id_admin=current_user.id_usuario,
        mensagem=mensagem,
        status_anterior=status_anterior,
        status_novo="finalizado",
        lida=False
    )

    db.session.add(atualizacao)

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


# =========================================================
# RELATÓRIOS
# =========================================================

def consultas_relatorio(parametros):
    """Aplica os mesmos filtros à tela e à exportação do relatório."""
    chamados = PedidoSOS.query
    denuncias = Denuncia.query
    data_inicio = parametros.get("data_inicio", "").strip()
    data_fim = parametros.get("data_fim", "").strip()
    status = parametros.get("status", "").strip()

    try:
        if data_inicio:
            inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            chamados = chamados.filter(PedidoSOS.data_hora >= inicio)
            denuncias = denuncias.filter(Denuncia.data >= inicio)
        if data_fim:
            fim = datetime.strptime(data_fim, "%Y-%m-%d") + timedelta(days=1)
            chamados = chamados.filter(PedidoSOS.data_hora < fim)
            denuncias = denuncias.filter(Denuncia.data < fim)
    except ValueError:
        data_inicio = ""
        data_fim = ""

    if status in {"pendente", "em_andamento", "finalizado", "cancelado"}:
        denuncias = denuncias.filter(Denuncia.status == status)
        status_sos = "ativo" if status == "pendente" else status
        chamados = chamados.filter(PedidoSOS.status == status_sos)

    return chamados, denuncias, data_inicio, data_fim, status

@admin.route("/relatorios")
@login_required
def relatorios():

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    consultas = consultas_relatorio(request.args)
    consulta_chamados, consulta_denuncias, data_inicio, data_fim, filtro_status = consultas

    total_chamados = consulta_chamados.count()

    chamados_ativos = consulta_chamados.filter_by(
        status="ativo"
    ).count()

    chamados_andamento = consulta_chamados.filter_by(
        status="em_andamento"
    ).count()

    chamados_finalizados = consulta_chamados.filter_by(
        status="finalizado"
    ).count()

    # =====================================================
    # DENÚNCIAS
    # =====================================================

    total_denuncias = consulta_denuncias.count()

    denuncias_pendentes = consulta_denuncias.filter_by(
        status="pendente"
    ).count()

    denuncias_andamento = consulta_denuncias.filter_by(
        status="em_andamento"
    ).count()

    denuncias_finalizadas = consulta_denuncias.filter_by(
        status="finalizado"
    ).count()

    # =====================================================
    # USUÁRIOS
    # =====================================================

    total_usuarios = Usuario.query.count()

    # =====================================================
    # TOTAIS
    # =====================================================

    total_andamento = (
        chamados_andamento
        + denuncias_andamento
    )

    total_finalizados = (
        chamados_finalizados
        + denuncias_finalizadas
    )

    ocorrencias_totais = (
        total_chamados
        + total_denuncias
    )

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

        ocorrencias_totais=ocorrencias_totais,
        data_inicio=data_inicio,
        data_fim=data_fim,
        filtro_status=filtro_status
    )


@admin.route("/relatorios/exportar-csv")
@login_required
def exportar_relatorio_csv():
    if not usuario_e_admin():
        return redirect(url_for("home.index"))

    chamados, denuncias, _, _, _ = consultas_relatorio(request.args)
    buffer = StringIO()
    escritor = csv.writer(buffer, delimiter=";")
    escritor.writerow(["Tipo", "Protocolo", "Data", "Status", "Descrição"])
    for chamado in chamados.order_by(PedidoSOS.data_hora.desc()).all():
        escritor.writerow([
            "Alerta SOS", f"SOS #{chamado.id_sos:06d}",
            chamado.data_hora.strftime("%d/%m/%Y %H:%M"), chamado.status,
            chamado.observacao_encaminhamento or "Alerta registrado"
        ])
    for denuncia_item in denuncias.order_by(Denuncia.data.desc()).all():
        escritor.writerow([
            "Denúncia", f"#{denuncia_item.id_denuncia:06d}",
            denuncia_item.data.strftime("%d/%m/%Y %H:%M"), denuncia_item.status,
            denuncia_item.titulo
        ])

    arquivo = BytesIO(buffer.getvalue().encode("utf-8-sig"))
    return send_file(
        arquivo,
        mimetype="text/csv",
        as_attachment=True,
        download_name="relatorio-sosmulher.csv"
    )


# =========================================================
# CONFIGURAÇÕES
# =========================================================

@admin.route("/configuracoes")
@login_required
def configuracoes():

    if not usuario_e_admin():

        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    return render_template(
        "admin/configuracoes.html"
    )
