from sosmulher import db, bcrypt

from sosmulher.models.usuario import Usuario

def cadastrar_usuario(form):

    senha = bcrypt.generate_password_hash(form.senha.data).decode("utf-8")
    usuario = Usuario( nome=form.nome.data, email=form.email.data, cpf=form.cpf.data, telefone=form.telefone.data, senha=senha)
    db.session.add(usuario)
    db.session.commit()

    return usuario

def autenticar_usuario(usuario, senha):

    return bcrypt.check_password_hash(usuario.senha, senha)

   