from sosmulher import db

from sosmulher.models.pedido_sos import PedidoSOS
from sosmulher.models.pedido_sos_contato import PedidoSOSContato
from sosmulher.models.contato_emergencia import ContatoEmergencia


# =========================================================
# CRIAR PEDIDO SOS
# =========================================================

def criar_pedido_sos(usuario, latitude, longitude):

    pedido = PedidoSOS(
        id_usuario=usuario.id_usuario,
        latitude=latitude,
        longitude=longitude,
        status="ativo"
    )

    db.session.add(pedido)

    # Gera o ID antes do commit
    db.session.flush()


    # Busca os contatos cadastrados pelo usuário
    contatos = ContatoEmergencia.query.filter_by(
        id_usuario=usuario.id_usuario
    ).all()


    # Vincula os contatos ao pedido SOS
    for contato in contatos:

        vinculo = PedidoSOSContato(
            id_sos=pedido.id_sos,
            id_contato=contato.id_contato
        )

        db.session.add(vinculo)


    db.session.commit()

    return pedido, len(contatos)


# =========================================================
# CANCELAR PEDIDO SOS
# =========================================================

def cancelar_pedido_sos(id_sos, id_usuario):

    pedido = PedidoSOS.query.filter_by(
        id_sos=id_sos,
        id_usuario=id_usuario
    ).first()


    if pedido is None:
        return None

    if pedido.status != "ativo":
        return False


    pedido.status = "cancelado"

    db.session.commit()

    return pedido


# =========================================================
# LISTAR HISTÓRICO DE SOS DO USUÁRIO
# =========================================================

def listar_pedidos_sos_usuario(id_usuario):

    return PedidoSOS.query.filter_by(
        id_usuario=id_usuario
    ).order_by(
        PedidoSOS.data_hora.desc()
    ).all()
