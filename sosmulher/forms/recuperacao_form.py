from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField
from wtforms.validators import DataRequired, Email


class RecuperacaoForm(FlaskForm):

    email = EmailField(
        "E-mail",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    submit = SubmitField("Enviar")