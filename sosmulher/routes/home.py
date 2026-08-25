from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required

from sosmulher.services.sos_service import (
    criar_pedido_sos,
    cancelar_pedido_sos
)


home = Blueprint("home", __name__)


# =========================================================
# INÍCIO
# =========================================================

@home.route("/")
def index():
    return render_template("index.html")


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

        if not pedido:
            return jsonify({
                "sucesso": False,
                "mensagem": "Pedido SOS não encontrado."
            }), 404

        return jsonify({
            "sucesso": True,
            "mensagem": "Alerta cancelado com sucesso.",
            "id_sos": pedido.id_sos,
            "status": pedido.status
        })

    except Exception as erro:

        print("Erro ao cancelar pedido SOS:", erro)

        return jsonify({
            "sucesso": False,
            "mensagem": "Não foi possível cancelar o alerta."
        }), 500