from flask import Blueprint, render_template
from flask_login import login_required, current_user

from sosmulher.services.sos_service import (
    listar_pedidos_sos_usuario
)


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