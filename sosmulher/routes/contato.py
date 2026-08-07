from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from sosmulher.forms import ContatoEmergenciaForm

from sosmulher.services.contato_service import (
    criar_contato,
    listar_contatos,
    buscar_contato,
    atualizar_contato,
    excluir_contato
)

contato = Blueprint("contato", __name__)


@contato.route("/contatos")
@login_required
def contatos():

    contatos = listar_contatos(current_user)

    return render_template(
        "contatos.html",
        contatos=contatos
    )


@contato.route("/adicionar-contato", methods=["GET", "POST"])
@login_required
def adicionar_contato():

    form = ContatoEmergenciaForm()

    if form.validate_on_submit():

        criar_contato(form, current_user)

        flash(
            "Contato cadastrado com sucesso!",
            "success"
        )

        return redirect(
            url_for("contato.contatos")
        )

    return render_template(
        "adicionar_contato.html",
        form=form
    )


@contato.route("/editar-contato/<int:id>", methods=["GET", "POST"])
@login_required
def editar_contato(id):

    contato = buscar_contato(
        id,
        current_user
    )

    if contato is None:

        flash(
            "Contato não encontrado.",
            "danger"
        )

        return redirect(
            url_for("contato.contatos")
        )

    form = ContatoEmergenciaForm(obj=contato)

    if form.validate_on_submit():

        atualizar_contato(
            contato,
            form
        )

        flash(
            "Contato atualizado com sucesso!",
            "success"
        )

        return redirect(
            url_for("contato.contatos")
        )

    return render_template(
        "editar_contato.html",
        form=form,
        contato=contato
    )


@contato.route("/excluir-contato/<int:id>")
@login_required
def excluir(id):

    contato = buscar_contato(
        id,
        current_user
    )

    if contato:

        excluir_contato(contato)

        flash(
            "Contato excluído com sucesso!",
            "success"
        )

    else:

        flash(
            "Contato não encontrado.",
            "danger"
        )

    return redirect(
        url_for("contato.contatos")
    )