
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from sosmulher import db
from sosmulher.models import (
    PedidoSOS,
    PedidoSOSContato,
    ContatoEmergencia
)

sos = Blueprint("sos", __name__)


# ==========================================================
# ACIONAR SOS
# ==========================================================

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

        # --------------------------------------------------
        # VERIFICA LOCALIZAÇÃO
        # --------------------------------------------------

        if latitude is None or longitude is None:

            return jsonify({
                "sucesso": False,
                "erro": "Localização não foi informada."
            }), 400


        # --------------------------------------------------
        # CRIA O PEDIDO SOS
        #
        # IMPORTANTE:
        # O chamado começa como EM ANDAMENTO.
        #
        # Ele só será FINALIZADO quando o administrador
        # clicar em "Acionar contatos de emergência".
        # --------------------------------------------------

        pedido = PedidoSOS(

            id_usuario=current_user.id_usuario,

            latitude=float(latitude),

            longitude=float(longitude),

            status="em_andamento"

        )

        db.session.add(pedido)

        # Gera o ID antes de criar os relacionamentos
        db.session.flush()


        # --------------------------------------------------
        # BUSCA OS CONTATOS DE EMERGÊNCIA
        # --------------------------------------------------

        contatos = ContatoEmergencia.query.filter_by(
            id_usuario=current_user.id_usuario
        ).all()

        print(
            "Contatos encontrados:",
            len(contatos)
        )


        # --------------------------------------------------
        # VINCULA OS CONTATOS AO PEDIDO
        #
        # ATENÇÃO:
        # Isso NÃO significa que eles foram acionados.
        #
        # Apenas registra quais contatos pertencem
        # àquele chamado.
        # --------------------------------------------------

        for contato in contatos:

            relacionamento = PedidoSOSContato(

                id_sos=pedido.id_sos,

                id_contato=contato.id_contato

            )

            db.session.add(relacionamento)


        # --------------------------------------------------
        # SALVA
        # --------------------------------------------------

        db.session.commit()


        print(
            "SOS registrado com sucesso!"
        )

        print(
            "ID do SOS:",
            pedido.id_sos
        )

        print(
            "Status:",
            pedido.status
        )


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

            "erro":
                "Erro interno ao registrar o pedido de emergência."

        }), 500



# ==========================================================
# CONSULTAR STATUS DO SOS
# ==========================================================

@sos.route("/sos/status/<int:id_sos>", methods=["GET"])
@login_required
def status_sos(id_sos):

    try:

        # --------------------------------------------------
        # PROCURA O SOS
        # --------------------------------------------------

        pedido = PedidoSOS.query.filter_by(
            id_sos=id_sos
        ).first()


        if not pedido:

            return jsonify({

                "sucesso": False,

                "erro": "Chamado SOS não encontrado."

            }), 404


        # --------------------------------------------------
        # SEGURANÇA
        #
        # A usuária só pode consultar os próprios chamados.
        # --------------------------------------------------

        if pedido.id_usuario != current_user.id_usuario:

            return jsonify({

                "sucesso": False,

                "erro": "Você não possui acesso a este chamado."

            }), 403


        # --------------------------------------------------
        # CONTATOS VINCULADOS
        # --------------------------------------------------

        quantidade_contatos = PedidoSOSContato.query.filter_by(
            id_sos=pedido.id_sos
        ).count()


        # --------------------------------------------------
        # RETORNA STATUS ATUAL
        # --------------------------------------------------

        return jsonify({

            "sucesso": True,

            "id_sos": pedido.id_sos,

            "status": pedido.status,

            "contatos": quantidade_contatos,

            "latitude": pedido.latitude,

            "longitude": pedido.longitude,

            "data_hora":
                pedido.data_hora.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

        }), 200


    except Exception as erro:

        print("===================================")
        print("ERRO AO CONSULTAR STATUS DO SOS")
        print("===================================")
        print(erro)
        print("===================================")


        return jsonify({

            "sucesso": False,

            "erro":
                "Erro interno ao consultar o status do chamado."

        }), 500

