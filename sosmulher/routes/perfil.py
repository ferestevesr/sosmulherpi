from flask import Blueprint, render_template
from flask_login import login_required


perfil = Blueprint(
    "perfil",
    __name__
)


@perfil.route("/perfil")
@login_required
def perfil_page():

    return render_template(
        "perfil.html"
    )