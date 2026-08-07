from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sosmulher.forms import DenunciaForm
from sosmulher.services.denuncia_service import criar_denuncia

denuncia = Blueprint("denuncia", __name__)

@denuncia.route("/denuncia", methods=["GET", "POST"])
@login_required
def denunciar():

    print("MÉTODO:", request.method)

    form = DenunciaForm()

    if request.method == "POST":

        print("POST CHEGOU")

        if form.validate():

            print("FORM VALIDOU")

            criar_denuncia(form, current_user)

            flash(
                "Denúncia enviada com sucesso!",
                "success"
            )

            return redirect(url_for("home.index"))

        else:
            print("ERROS:", form.errors)

    return render_template(
        "denuncia.html",
        form=form
    )