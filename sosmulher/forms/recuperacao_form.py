from flask_wtf import FlaskForm

from wtforms import (
    EmailField,
    StringField,
    PasswordField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length
)


class RecuperacaoForm(FlaskForm):

    email = EmailField(
        "E-mail",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    submit = SubmitField(
        "Enviar código"
    )


class CodigoRecuperacaoForm(FlaskForm):

    codigo = StringField(
        "Código de verificação",
        validators=[
            DataRequired(),
            Length(
                min=6,
                max=6,
                message="O código deve possuir 6 números."
            )
        ]
    )

    submit = SubmitField(
        "Verificar código"
    )


class NovaSenhaForm(FlaskForm):

    senha = PasswordField(
        "Nova senha",
        validators=[
            DataRequired(),
            Length(
                min=8,
                max=128,
                message="A senha deve possuir entre 8 e 128 caracteres."
            )
        ]
    )

    confirmar_senha = PasswordField(
        "Confirmar nova senha",
        validators=[
            DataRequired(),
            EqualTo(
                "senha",
                message="As senhas precisam ser iguais."
            )
        ]
    )

    submit = SubmitField(
        "Alterar senha"
    )
