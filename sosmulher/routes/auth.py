from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from sosmulher.forms import LoginForm, CadastroForm
from sosmulher.models import Usuario
from sosmulher.services.auth_service import (cadastrar_usuario, autenticar_usuario)
from sosmulher import app
from flask import Blueprint


auth = Blueprint("auth", __name__)

@auth.route("/cadastro", methods=["GET","POST"])
def cadastro():

    form = CadastroForm()

    if form.validate_on_submit():

        cadastrar_usuario(form)

        flash(
            "Usuário cadastrado com sucesso!",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template(
        "cadastro.html",
        form=form
    )

@auth.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    form = LoginForm()

    if form.validate_on_submit():

        usuario=Usuario.query.filter_by(email=form.email.data).first()

        if usuario and autenticar_usuario(usuario, form.senha.data):

            login_user(usuario)
            flash(f"Bem-vindo(a), {usuario.nome}!","success")
            return redirect(url_for("home.index"))

    return render_template("login.html", form=form)



@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Logout realizado com sucesso",
        "info"
    )

    return redirect(url_for("home.index"))