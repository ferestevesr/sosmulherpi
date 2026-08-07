from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sosmulher.forms import DenunciaForm
from sosmulher.services.denuncia_service import criar_denuncia

denuncia = Blueprint("denuncia", __name__)


@denuncia.route("/denuncia", methods=["GET", "POST"])
@login_required
def denunciar():

    form = DenunciaForm()

    if form.validate_on_submit():

        print("ENTROU NO ENVIO")

        criar_denuncia(form, current_user)

        flash(
            "Denúncia enviada com sucesso!",
            "success"
        )

        return redirect(url_for("home.index"))

    else:
        print(form.errors)

    return render_template(
        "denuncia.html",
        form=form
    )