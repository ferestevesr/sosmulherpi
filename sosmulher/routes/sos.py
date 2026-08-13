from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from sosmulher import db
from sosmulher.models import (
    PedidoSOS,
    PedidoSOSContato,
    ContatoEmergencia
)

sos = Blueprint("sos", __name__)


@sos.route("/sos/acionar", methods=["POST"])
@login_required
def acionar_sos():

    try:

        dados = request.get_json()

        if not dados:
            return jsonify({
                "sucesso": False,
                "erro": "Nenhum dado foi enviado."
            }), 400

        latitude = dados.get("latitude")
        longitude = dados.get("longitude")

        print("=== DADOS RECEBIDOS NO SOS ===")
        print("Usuário:", current_user.id_usuario)
        print("Latitude:", latitude)
        print("Longitude:", longitude)

        # Verifica localização
        if latitude is None or longitude is None:
            return jsonify({
                "sucesso": False,
                "erro": "Localização não foi informada."
            }), 400

        # Cria o pedido SOS
        pedido = PedidoSOS(
            id_usuario=current_user.id_usuario,
            latitude=float(latitude),
            longitude=float(longitude),
            status="ativo"
        )

        db.session.add(pedido)

        # Gera o ID do pedido
        db.session.flush()

        # Busca os contatos de emergência
        contatos = ContatoEmergencia.query.filter_by(
            id_usuario=current_user.id_usuario
        ).all()

        print("Contatos encontrados:", len(contatos))

        # Relaciona os contatos ao pedido SOS
        for contato in contatos:

            relacionamento = PedidoSOSContato(
                id_sos=pedido.id_sos,
                id_contato=contato.id_contato
            )

            db.session.add(relacionamento)

        db.session.commit()

        print("SOS registrado com sucesso!")
        print("ID do SOS:", pedido.id_sos)

        return jsonify({
            "sucesso": True,
            "id_sos": pedido.id_sos,
            "contatos": len(contatos),
            "status": pedido.status,
            "latitude": pedido.latitude,
            "longitude": pedido.longitude
        }), 200

    except Exception as erro:

        db.session.rollback()

        print("===================================")
        print("ERRO AO REGISTRAR SOS")
        print("===================================")
        print(erro)
        print("===================================")

        return jsonify({
            "sucesso": False,
            "erro": "Erro interno ao registrar o pedido de emergência."
        }), 500