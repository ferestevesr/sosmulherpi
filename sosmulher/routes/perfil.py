from flask import Blueprint, render_template
from flask_login import login_required, current_user

from sosmulher.services.sos_service import (
    listar_pedidos_sos_usuario
)
from sosmulher.models.pedido_sos import PedidoSOS
from sosmulher.models.atualizacao_sos import AtualizacaoSOS


perfil = Blueprint(
    "perfil",
    __name__
)


@perfil.route("/perfil")
@login_required
def perfil_page():

    pedidos_sos = listar_pedidos_sos_usuario(
        current_user.id_usuario
    )

    return render_template(
        "perfil.html",
        pedidos_sos=pedidos_sos
    )


@perfil.route("/sos/<int:id_sos>")
@login_required
def detalhes_sos(id_sos):
    pedido = PedidoSOS.query.filter_by(
        id_sos=id_sos,
        id_usuario=current_user.id_usuario
    ).first_or_404()
    atualizacoes = (
        AtualizacaoSOS.query
        .filter_by(id_sos=pedido.id_sos)
        .order_by(AtualizacaoSOS.data.asc())
        .all()
    )
    return render_template(
        "detalhes_sos.html",
        pedido=pedido,
        atualizacoes=atualizacoes
    )
