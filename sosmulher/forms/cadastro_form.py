from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    EmailField,
    PasswordField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Regexp
)

from sosmulher.forms.validators import (
    validar_email,
    validar_cpf
)


class CadastroForm(FlaskForm):

    nome = StringField(
        "Nome",
        validators=[
            DataRequired(
                message="Informe seu nome."
            ),
            Length(
                min=2,
                max=100,
                message="O nome deve possuir entre 2 e 100 caracteres."
            )
        ]
    )

    email = EmailField(
        "E-mail",
        validators=[
            DataRequired(
                message="Informe seu e-mail."
            ),
            Email(
                message="Digite um e-mail válido."
            ),
            Length(
                max=100,
                message="O e-mail é muito longo."
            ),
            validar_email
        ]
    )

    cpf = StringField(
        "CPF",
        validators=[
            DataRequired(
                message="Informe seu CPF."
            ),
            validar_cpf
        ]
    )

    telefone = StringField(
        "Telefone",
        validators=[
            DataRequired(
                message="Informe seu telefone."
            ),
            Regexp(
                r"^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$",
                message="Digite um telefone válido com DDD."
            )
        ]
    )

    senha = PasswordField(
        "Senha",
        validators=[
            DataRequired(
                message="Crie uma senha."
            ),
            Length(
                min=6,
                max=255,
                message="A senha deve possuir pelo menos 6 caracteres."
            )
        ]
    )

    confirmar_senha = PasswordField(
        "Confirmar Senha",
        validators=[
            DataRequired(
                message="Confirme sua senha."
            ),
            EqualTo(
                "senha",
                message="As senhas precisam ser iguais."
            )
        ]
    )

    botao_cadastro = SubmitField(
        "Cadastrar"
    )