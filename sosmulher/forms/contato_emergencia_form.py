from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ContatoEmergenciaForm(FlaskForm):

    nome = StringField(
        "Nome",
        validators=[DataRequired()]
    )

    telefone = StringField(
        "Telefone",
        validators=[DataRequired()]
    )

    parentesco = StringField(
        "Parentesco",
        validators=[DataRequired()]
    )

    botao_salvar = SubmitField("Salvar")