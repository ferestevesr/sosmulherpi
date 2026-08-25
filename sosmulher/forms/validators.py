import re

from wtforms.validators import ValidationError

from sosmulher.models.usuario import Usuario


# =========================================================
# FUNÇÃO AUXILIAR
# =========================================================

def somente_numeros(valor):

    if not valor:
        return ""

    return re.sub(r"\D", "", valor)


# =========================================================
# VALIDAR E-MAIL
# =========================================================

def validar_email(form, campo):

    email = campo.data.strip().lower()

    usuario = Usuario.query.filter_by(
        email=email
    ).first()

    if usuario:
        raise ValidationError(
            "E-mail já cadastrado. Por favor, utilize outro e-mail."
        )


# =========================================================
# VALIDAR CPF
# =========================================================

def validar_cpf(form, campo):

    cpf = somente_numeros(
        campo.data
    )

    # CPF precisa ter exatamente 11 números
    if len(cpf) != 11:
        raise ValidationError(
            "Digite um CPF válido."
        )

    # Impede CPFs com todos os números iguais
    if cpf == cpf[0] * 11:
        raise ValidationError(
            "Digite um CPF válido."
        )

    # -----------------------------------------------------
    # PRIMEIRO DÍGITO VERIFICADOR
    # -----------------------------------------------------

    soma = 0

    for indice in range(9):
        soma += int(cpf[indice]) * (10 - indice)

    resto = soma % 11

    primeiro_digito = (
        0 if resto < 2 else 11 - resto
    )

    if int(cpf[9]) != primeiro_digito:
        raise ValidationError(
            "Digite um CPF válido."
        )

    # -----------------------------------------------------
    # SEGUNDO DÍGITO VERIFICADOR
    # -----------------------------------------------------

    soma = 0

    for indice in range(10):
        soma += int(cpf[indice]) * (11 - indice)

    resto = soma % 11

    segundo_digito = (
        0 if resto < 2 else 11 - resto
    )

    if int(cpf[10]) != segundo_digito:
        raise ValidationError(
            "Digite um CPF válido."
        )

    # -----------------------------------------------------
    # VERIFICAR SE JÁ EXISTE
    # -----------------------------------------------------

    usuario = Usuario.query.filter_by(
        cpf=cpf
    ).first()

    if usuario:
        raise ValidationError(
            "CPF já cadastrado. Por favor, utilize outro CPF."
        )