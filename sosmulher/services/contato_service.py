from sosmulher import db
from sosmulher.models import ContatoEmergencia


def criar_contato(form, usuario):

    contato = ContatoEmergencia(
        id_usuario=usuario.id_usuario,
        nome=form.nome.data,
        telefone=form.telefone.data,
        parentesco=form.parentesco.data
    )

    db.session.add(contato)
    db.session.commit()

    return contato


def listar_contatos(usuario):

    return ContatoEmergencia.query.filter_by(
        id_usuario=usuario.id_usuario
    ).all()


def buscar_contato(id_contato, usuario):

    return ContatoEmergencia.query.filter_by(
        id_contato=id_contato,
        id_usuario=usuario.id_usuario
    ).first()


def atualizar_contato(contato, form):

    contato.nome = form.nome.data
    contato.telefone = form.telefone.data
    contato.parentesco = form.parentesco.data

    db.session.commit()

    return contato


def excluir_contato(contato):

    db.session.delete(contato)
    db.session.commit()