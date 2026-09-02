from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField

from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    BooleanField,
    SubmitField
)

from wtforms.validators import DataRequired, InputRequired


class DenunciaForm(FlaskForm):

    titulo = StringField(
        "Título",
        validators=[
            DataRequired()
        ]
    )

    descricao = TextAreaField(
        "Descrição",
        validators=[
            DataRequired()
        ]
    )

    tipo = SelectField(
        "Tipo de Violência",
        choices=[
            (
                "violencia_fisica",
                "Violência Física"
            ),
            (
                "violencia_psicologica",
                "Violência Psicológica"
            ),
            (
                "violencia_sexual",
                "Violência Sexual"
            ),
            (
                "assedio",
                "Assédio"
            ),
            (
                "ameaca",
                "Ameaça"
            ),
            (
                "outro",
                "Outro"
            )
        ],
        validators=[
            DataRequired()
        ]
    )

    nivel_risco = SelectField(
        "Nível de risco",
        choices=[
            (
                "baixo",
                "Baixo"
            ),
            (
                "medio",
                "Médio"
            ),
            (
                "alto",
                "Alto"
            ),
            (
                "emergencia",
                "Emergência"
            )
        ],
        validators=[
            DataRequired()
        ]
    )

    anonimo = BooleanField(
        "Denúncia Anônima"
    )

    confirmacao = BooleanField(
        "Confirmo que as informações fornecidas são verdadeiras.",
        validators=[InputRequired("Confirme as informações antes de enviar.")]
    )

    arquivo = FileField(
        "Anexar Arquivo",
        validators=[
            FileAllowed(
                [
                    "jpg",
                    "jpeg",
                    "png",
                    "mp4",
                    "pdf",
                    "doc",
                    "docx"
                ],
                "Formato inválido."
            )
        ]
    )

    botao_enviar = SubmitField(
        "Enviar Denúncia"
    )
