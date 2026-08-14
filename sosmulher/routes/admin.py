from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from sosmulher.models.usuario import Usuario
from sosmulher.models.denuncia import Denuncia


admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


@admin.route("/")
@login_required
def dashboard():

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    total_usuarios = Usuario.query.count()

    total_denuncias = Denuncia.query.count()

    denuncias_pendentes = Denuncia.query.filter_by(
        status="pendente"
    ).count()

    denuncias_andamento = Denuncia.query.filter_by(
        status="em_andamento"
    ).count()

    denuncias_finalizadas = Denuncia.query.filter_by(
        status="finalizado"
    ).count()

    denuncias_recentes = Denuncia.query.order_by(
        Denuncia.data.desc()
    ).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_usuarios=total_usuarios,
        total_denuncias=total_denuncias,
        denuncias_pendentes=denuncias_pendentes,
        denuncias_andamento=denuncias_andamento,
        denuncias_finalizadas=denuncias_finalizadas
    )





# ==========================
# USUÁRIOS
# ==========================

@admin.route("/usuarios")
@login_required
def usuarios():

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    return render_template("admin/usuarios.html")


# ==========================
# CHAMADOS
# ==========================

@admin.route("/chamados")
@login_required
def chamados():

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    return render_template("admin/chamados.html")


# ==========================
# ATENDIMENTO
# ==========================

@admin.route("/atendimento")
@login_required
def atendimento():

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    return render_template("admin/atendimento.html")


# ==========================
# RELATÓRIOS
# ==========================

@admin.route("/relatorios")
@login_required
def relatorios():

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    return render_template("admin/relatorios.html")


# ==========================
# CONFIGURAÇÕES
# ==========================

@admin.route("/configuracoes")
@login_required
def configuracoes():

    if current_user.tipo != "admin":
        flash(
            "Você não tem permissão para acessar esta página.",
            "danger"
        )
        return redirect(url_for("home.index"))

    return render_template("admin/configuracoes.html")