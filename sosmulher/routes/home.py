from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required

from sosmulher.services.sos_service import (
    criar_pedido_sos,
    cancelar_pedido_sos
)
from sosmulher.models.pedido_sos import PedidoSOS
from sosmulher.models.denuncia import Denuncia
from sosmulher.models.atualizacao_denuncia import AtualizacaoDenuncia
from sosmulher.models.atualizacao_sos import AtualizacaoSOS


home = Blueprint("home", __name__)


# =========================================================
# INÍCIO
# =========================================================

@home.route("/")
def index():
    return render_template("index.html")


@home.route("/minha-area")
@login_required
def minha_area():
    """Painel resumido da usuária com os atendimentos mais recentes."""
    if current_user.tipo == "admin":
        return redirect(url_for("admin.dashboard"))

    denuncias = (
        Denuncia.query
        .filter_by(id_usuario=current_user.id_usuario)
        .order_by(Denuncia.data.desc())
        .all()
    )
    pedidos_sos = (
        PedidoSOS.query
        .filter_by(id_usuario=current_user.id_usuario)
        .order_by(PedidoSOS.data_hora.desc())
        .all()
    )

    itens_recentes = [
        {
            "id": denuncia.id_denuncia,
            "titulo": denuncia.titulo,
            "tipo": "Denúncia",
            "status": denuncia.status,
            "data": denuncia.data,
            "url": url_for(
                "denuncia.detalhes_denuncia",
                id_denuncia=denuncia.id_denuncia
            )
        }
        for denuncia in denuncias
    ] + [
        {
            "id": pedido.id_sos,
            "titulo": "Alerta SOS",
            "tipo": "SOS",
            "status": pedido.status,
            "data": pedido.data_hora,
            "url": url_for("perfil.perfil_page")
        }
        for pedido in pedidos_sos
    ]
    itens_recentes.sort(key=lambda item: item["data"], reverse=True)

    em_andamento = sum(
        item.status == "em_andamento" for item in denuncias
    ) + sum(item.status == "em_andamento" for item in pedidos_sos)
    finalizados = sum(
        item.status == "finalizado" for item in denuncias
    ) + sum(item.status == "finalizado" for item in pedidos_sos)

    notificacoes_nao_lidas = (
        AtualizacaoDenuncia.query
        .join(Denuncia)
        .filter(Denuncia.id_usuario == current_user.id_usuario)
        .filter(AtualizacaoDenuncia.lida.is_(False))
        .count()
        + AtualizacaoSOS.query
        .join(PedidoSOS)
        .filter(PedidoSOS.id_usuario == current_user.id_usuario)
        .filter(AtualizacaoSOS.lida.is_(False))
        .count()
    )

    return render_template(
        "minha_area.html",
        itens_recentes=itens_recentes[:5],
        em_andamento=em_andamento,
        finalizados=finalizados,
        notificacoes_nao_lidas=notificacoes_nao_lidas
    )


# =========================================================
# APOIO
# =========================================================

@home.route("/apoio")
def apoio():
    return render_template("apoio.html")


# =========================================================
# SOS
# =========================================================

@home.route("/sos")
@login_required
def sos():
    return render_template("sos.html")


# =========================================================
# AJUDA
# =========================================================

@home.route("/ajuda")
def ajuda():
    return render_template("ajuda.html")


# =========================================================
# SOBRE
# =========================================================

@home.route("/sobre")
def sobre():
    return render_template("sobre.html")

# =========================================================
# POLÍTICA DE PRIVACIDADE
# =========================================================
@home.route("/politica-privacidade")
def politica_privacidade():
    return render_template("politica_privacidade.html")


# =========================================================
# TERMOS DE USO
# =========================================================
@home.route("/termos-de-uso")
def termos_uso():
    return render_template("termos_uso.html")

# =========================================================
# CRIAR PEDIDO SOS
# =========================================================

@home.route("/api/sos", methods=["POST"])
@login_required
def criar_sos_api():

    dados = request.get_json(silent=True) or {}

    latitude = dados.get("latitude")
    longitude = dados.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({
            "sucesso": False,
            "mensagem": "Localização não informada."
        }), 400

    try:
        latitude = float(latitude)
        longitude = float(longitude)

    except (TypeError, ValueError):
        return jsonify({
            "sucesso": False,
            "mensagem": "Localização inválida."
        }), 400

    if latitude < -90 or latitude > 90:
        return jsonify({
            "sucesso": False,
            "mensagem": "Latitude inválida."
        }), 400

    if longitude < -180 or longitude > 180:
        return jsonify({
            "sucesso": False,
            "mensagem": "Longitude inválida."
        }), 400

    alerta_aberto = PedidoSOS.query.filter(
        PedidoSOS.id_usuario == current_user.id_usuario,
        PedidoSOS.status.in_(["ativo", "em_andamento"])
    ).order_by(PedidoSOS.data_hora.desc()).first()

    if alerta_aberto:
        return jsonify({
            "sucesso": False,
            "mensagem": "Já existe um alerta SOS em acompanhamento.",
            "id_sos": alerta_aberto.id_sos,
            "status": alerta_aberto.status
        }), 409

    try:

        pedido, quantidade_contatos = criar_pedido_sos(
            current_user,
            latitude,
            longitude
        )

        return jsonify({
            "sucesso": True,
            "mensagem": "Alerta registrado com sucesso.",
            "id_sos": pedido.id_sos,
            "status": pedido.status,
            "contatos": quantidade_contatos
        }), 201

    except Exception as erro:

        print("Erro ao criar pedido SOS:", erro)

        db.session.rollback()

        return jsonify({
            "sucesso": False,
            "mensagem": "Não foi possível registrar o alerta."
        }), 500


# =========================================================
# CANCELAR PEDIDO SOS
# =========================================================

@home.route("/api/sos/cancelar", methods=["POST"])
@login_required
def cancelar_sos_api():

    dados = request.get_json(silent=True) or {}

    id_sos = dados.get("id_sos")

    if id_sos is None:
        return jsonify({
            "sucesso": False,
            "mensagem": "Pedido SOS não informado."
        }), 400

    try:
        id_sos = int(id_sos)

    except (TypeError, ValueError):
        return jsonify({
            "sucesso": False,
            "mensagem": "Pedido SOS inválido."
        }), 400

    try:

        pedido = cancelar_pedido_sos(
            id_sos,
            current_user.id_usuario
        )

        if pedido is None:
            return jsonify({
                "sucesso": False,
                "mensagem": "Pedido SOS não encontrado."
            }), 404

        if pedido is False:
            return jsonify({
                "sucesso": False,
                "mensagem": "Este alerta já está em atendimento ou foi finalizado e não pode ser cancelado."
            }), 409

        return jsonify({
            "sucesso": True,
            "mensagem": "Alerta cancelado com sucesso.",
            "id_sos": pedido.id_sos,
            "status": pedido.status
        })

    except Exception as erro:

        print("Erro ao cancelar pedido SOS:", erro)

        db.session.rollback()

        return jsonify({
            "sucesso": False,
            "mensagem": "Não foi possível cancelar o alerta."
        }), 500


@home.route("/api/sos/<int:id_sos>")
@login_required
def status_sos_api(id_sos):
    """Permite à usuária acompanhar exclusivamente o próprio alerta."""
    pedido = PedidoSOS.query.filter_by(
        id_sos=id_sos,
        id_usuario=current_user.id_usuario
    ).first()

    if pedido is None:
        return jsonify({"sucesso": False, "mensagem": "Alerta não encontrado."}), 404

    return jsonify({
        "sucesso": True,
        "id_sos": pedido.id_sos,
        "status": pedido.status,
        "atualizado_em": pedido.atualizacoes[-1].data.isoformat()
        if pedido.atualizacoes else None
    })
