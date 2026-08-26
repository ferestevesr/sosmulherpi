from sosmulher import db
from sosmulher.models.notificacao import Notificacao


def criar_notificacao(
    id_usuario,
    titulo,
    mensagem,
    tipo,
    id_denuncia=None
):

    notificacao = Notificacao(
        id_usuario=id_usuario,
        id_denuncia=id_denuncia,
        titulo=titulo,
        mensagem=mensagem,
        tipo=tipo
    )

    db.session.add(notificacao)

    return notificacao