from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    BooleanField,
    SubmitField
)
from wtforms.validators import DataRequired


class DenunciaForm(FlaskForm):

    titulo = StringField(
        "Título",
        validators=[DataRequired()]
    )

    descricao = TextAreaField(
        "Descrição",
        validators=[DataRequired()]
    )

    tipo = SelectField(
        "Tipo de Violência",
        choices=[
            ("violencia_fisica", "Violência Física"),
            ("violencia_psicologica", "Violência Psicológica"),
            ("violencia_sexual", "Violência Sexual"),
            ("assedio", "Assédio"),
            ("ameaca", "Ameaça"),
            ("outro", "Outro")
        ], 
        validators=[DataRequired()]
    )

    nivel_risco = SelectField(
        "Nível de risco",
        choices=[
            ("baixo", "Baixo"),
            ("medio", "Médio"),
            ("alto", "Alto"),
            ("emergencia", "Emergência")
        ],
        validators=[DataRequired()]
    )

    anonimo = BooleanField("Denúncia Anônima")

    arquivo = FileField(
        "Anexar Arquivo",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "mp4", "mp3"],
                "Formato inválido."
            )
        ]
    )

    botao_enviar = SubmitField("Enviar Denúncia")