from wtforms.validators import ValidationError

from sosmulher.models.usuario import Usuario    

def validar_email(form, campo):

    usuario =Usuario.query.filter_by(email=campo.data).first()
    if usuario:
        raise ValidationError("E-mail já cadastrado. Por favor, utilize outro e-mail.")


def validar_cpf(form, campo):
    usuario = Usuario.query.filter_by(cpf=campo.data).first()
    if usuario:
        raise ValidationError("CPF já cadastrado. Por favor, utilize outro CPF.")