import secrets

from datetime import datetime, timedelta

from sosmulher import db, bcrypt

from sosmulher.models.recuperacao_conta import RecuperacaoConta


# =========================================================
# CRIAR CÓDIGO
# =========================================================

def criar_codigo_recuperacao(usuario):

    # Invalida códigos antigos ainda não utilizados
    recuperacoes_antigas = RecuperacaoConta.query.filter_by(
        id_usuario=usuario.id_usuario,
        utilizado=False
    ).all()

    for recuperacao in recuperacoes_antigas:
        recuperacao.utilizado = True


    # Código aleatório de 6 dígitos
    codigo = str(
        secrets.randbelow(900000) + 100000
    )


    # Guardamos hash do código no banco
    codigo_hash = bcrypt.generate_password_hash(
        codigo
    ).decode("utf-8")


    recuperacao = RecuperacaoConta(
        id_usuario=usuario.id_usuario,
        codigo=codigo_hash,
        data_expiracao=datetime.now() + timedelta(minutes=10),
        utilizado=False
    )


    db.session.add(recuperacao)

    db.session.commit()


    return recuperacao, codigo


# =========================================================
# VALIDAR CÓDIGO
# =========================================================

def validar_codigo_recuperacao(
    recuperacao,
    codigo
):

    if recuperacao is None:
        return False


    if recuperacao.utilizado:
        return False


    if recuperacao.data_expiracao < datetime.now():
        return False


    return bcrypt.check_password_hash(
        recuperacao.codigo,
        codigo
    )


# =========================================================
# ALTERAR SENHA
# =========================================================

def alterar_senha_recuperacao(
    usuario,
    nova_senha,
    recuperacao
):

    senha_hash = bcrypt.generate_password_hash(
        nova_senha
    ).decode("utf-8")


    usuario.senha = senha_hash

    recuperacao.utilizado = True


    db.session.commit()