from sosmulher import db
from sosmulher.models.denuncia import Denuncia


def criar_denuncia(form, usuario):

    denuncia = Denuncia(
        id_usuario=usuario.id_usuario,
        titulo=form.titulo.data,
        descricao=form.descricao.data,
        tipo=form.tipo.data,
        nivel_risco=form.nivel_risco.data,
        anonimo=form.anonimo.data
    )

    db.session.add(denuncia)

    db.session.commit()

    return denuncia


def listar_denuncias_usuario(id_usuario):

    return Denuncia.query.filter_by(
        id_usuario=id_usuario
    ).order_by(
        Denuncia.data.desc()
    ).all()