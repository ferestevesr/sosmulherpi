from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from sosmulher.forms.validators import validar_email, validar_cpf

class CadastroForm(FlaskForm):
    nome = StringField(
        "Nome", validators=[DataRequired(), Length(min=2, max=100)]
    )
    email = EmailField(
        "E-mail", validators=[DataRequired(), Email(), Length(max=100), validar_email]
    )
    cpf = StringField(
        "CPF", validators=[DataRequired(), Length(min=11, max=14), validar_cpf]
    )
    telefone = StringField(
        "Telefone", validators=[DataRequired(), Length(min=10, max=20)]
    )
    senha = PasswordField(
        "Senha", validators=[DataRequired(), Length(min=6, max=255)]
    )
    confirmar_senha = PasswordField(
        "Confirmar Senha", validators=[DataRequired(), EqualTo("senha")]
    )
    botao_cadastro = SubmitField("Cadastrar")