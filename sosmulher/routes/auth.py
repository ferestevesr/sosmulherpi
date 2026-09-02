from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    Blueprint,
    session
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from sosmulher.forms import (
    LoginForm,
    CadastroForm,
    RecuperacaoForm,
    CodigoRecuperacaoForm,
    NovaSenhaForm
)

from sosmulher.models import Usuario

from sosmulher.models.recuperacao_conta import (
    RecuperacaoConta
)

from sosmulher.services.auth_service import (
    cadastrar_usuario,
    autenticar_usuario
)

from sosmulher.services.recuperacao_service import (
    criar_codigo_recuperacao,
    validar_codigo_recuperacao,
    alterar_senha_recuperacao
)

from sosmulher.services.email_service import (
    enviar_email
)


auth = Blueprint(
    "auth",
    __name__
)


# =========================================================
# CADASTRO
# =========================================================

@auth.route(
    "/cadastro",
    methods=["GET", "POST"]
)
def cadastro():

    form = CadastroForm()


    if form.validate_on_submit():

        cadastrar_usuario(form)

        flash(
            "Usuário cadastrado com sucesso!",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )


    return render_template(
        "cadastro.html",
        form=form
    )


# =========================================================
# LOGIN
# =========================================================

@auth.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for("home.index")
        )


    form = LoginForm()


    if form.validate_on_submit():

        usuario = Usuario.query.filter_by(
            email=form.email.data
        ).first()


        if (
            usuario
            and usuario.status_conta == "ativa"
            and autenticar_usuario(usuario, form.senha.data)
        ):

            login_user(usuario)

            flash(
                f"Bem-vindo(a), {usuario.nome}!",
                "success"
            )

            return redirect(
                url_for("home.index")
            )


        flash(
            "E-mail ou senha inválidos.",
            "danger"
        )


    return render_template(
        "login.html",
        form=form
    )


# =========================================================
# RECUPERAÇÃO - INFORMAR E-MAIL
# =========================================================

@auth.route(
    "/recuperar-conta",
    methods=["GET", "POST"]
)
def recuperar_conta():

    form = RecuperacaoForm()


    if form.validate_on_submit():

        # Uma nova solicitação sempre começa sem tentativas anteriores.
        session.pop("recuperacao_tentativas", None)

        usuario = Usuario.query.filter_by(
            email=form.email.data
        ).first()


        # Resposta genérica para não revelar
        # se determinado e-mail possui conta.
        if usuario:

            try:

                recuperacao, codigo = (
                    criar_codigo_recuperacao(
                        usuario
                    )
                )


                mensagem = f"""
Olá, {usuario.nome}.

Recebemos uma solicitação para redefinir a senha da sua conta no SOSMulher.

Seu código de verificação é:

{codigo}

O código é válido por 10 minutos.

Se você não solicitou a alteração da senha, ignore esta mensagem.
"""


                enviar_email(
                    usuario.email,
                    "Código de recuperação - SOSMulher",
                    mensagem
                )


                session[
                    "recuperacao_id"
                ] = recuperacao.id_recuperacao


            except Exception as erro:

                print(
                    "Erro ao enviar recuperação:",
                    erro
                )

                flash(
                    "Não foi possível enviar o código neste momento.",
                    "danger"
                )

                return render_template(
                    "auth/recuperar.html",
                    form=form
                )


        flash(
            "Se o e-mail estiver cadastrado, um código de recuperação será enviado.",
            "success"
        )


        if usuario:

            return redirect(
                url_for(
                    "auth.verificar_codigo"
                )
            )


        return redirect(
            url_for("auth.login")
        )


    return render_template(
        "auth/recuperar.html",
        form=form
    )


# =========================================================
# RECUPERAÇÃO - VERIFICAR CÓDIGO
# =========================================================

@auth.route(
    "/verificar-codigo",
    methods=["GET", "POST"]
)
def verificar_codigo():

    recuperacao_id = session.get(
        "recuperacao_id"
    )


    if not recuperacao_id:

        flash(
            "Solicite um novo código de recuperação.",
            "warning"
        )

        return redirect(
            url_for(
                "auth.recuperar_conta"
            )
        )


    recuperacao = RecuperacaoConta.query.get(
        recuperacao_id
    )


    if recuperacao is None:

        session.pop(
            "recuperacao_id",
            None
        )

        return redirect(
            url_for(
                "auth.recuperar_conta"
            )
        )


    form = CodigoRecuperacaoForm()


    if form.validate_on_submit():

        tentativas = session.get("recuperacao_tentativas", 0)

        if tentativas >= 5:
            session.pop("recuperacao_id", None)
            session.pop("codigo_validado", None)
            session.pop("recuperacao_tentativas", None)
            flash("Muitas tentativas. Solicite um novo código.", "warning")
            return redirect(url_for("auth.recuperar_conta"))

        if validar_codigo_recuperacao(
            recuperacao,
            form.codigo.data
        ):

            session[
                "codigo_validado"
            ] = True
            session.pop("recuperacao_tentativas", None)


            return redirect(
                url_for(
                    "auth.nova_senha"
                )
            )


        session["recuperacao_tentativas"] = tentativas + 1

        flash(
            "Código inválido ou expirado.",
            "danger"
        )


    return render_template(
        "auth/verificar_codigo.html",
        form=form
    )


# =========================================================
# RECUPERAÇÃO - NOVA SENHA
# =========================================================

@auth.route(
    "/nova-senha",
    methods=["GET", "POST"]
)
def nova_senha():

    recuperacao_id = session.get(
        "recuperacao_id"
    )

    codigo_validado = session.get(
        "codigo_validado"
    )


    if (
        not recuperacao_id
        or not codigo_validado
    ):

        return redirect(
            url_for(
                "auth.recuperar_conta"
            )
        )


    recuperacao = RecuperacaoConta.query.get(
        recuperacao_id
    )


    if (
        recuperacao is None
        or recuperacao.utilizado
    ):

        session.pop(
            "recuperacao_id",
            None
        )

        session.pop(
            "codigo_validado",
            None
        )
        session.pop(
            "recuperacao_tentativas",
            None
        )

        return redirect(
            url_for(
                "auth.recuperar_conta"
            )
        )


    usuario = Usuario.query.get(
        recuperacao.id_usuario
    )


    if usuario is None:

        return redirect(
            url_for(
                "auth.recuperar_conta"
            )
        )


    form = NovaSenhaForm()


    if form.validate_on_submit():

        alterar_senha_recuperacao(
            usuario,
            form.senha.data,
            recuperacao
        )


        session.pop(
            "recuperacao_id",
            None
        )

        session.pop(
            "codigo_validado",
            None
        )

        session.pop(
            "recuperacao_tentativas",
            None
        )


        flash(
            "Senha alterada com sucesso. Faça login com sua nova senha.",
            "success"
        )


        return redirect(
            url_for(
                "auth.login"
            )
        )


    return render_template(
        "auth/nova_senha.html",
        form=form
    )


# =========================================================
# LOGOUT
# =========================================================

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Logout realizado com sucesso",
        "info"
    )

    return redirect(
        url_for("home.index")
    )
