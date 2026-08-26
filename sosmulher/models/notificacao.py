from sosmulher import db


class Notificacao(db.Model):

    __tablename__ = "Notificacao"

    id_notificacao = db.Column(
        db.Integer,
        primary_key=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("Usuario.id_usuario"),
        nullable=False
    )

    id_denuncia = db.Column(
        db.Integer,
        db.ForeignKey("Denuncia.id_denuncia"),
        nullable=True
    )

    titulo = db.Column(
        db.String(100),
        nullable=False
    )

    mensagem = db.Column(
        db.String(255),
        nullable=False
    )

    tipo = db.Column(
        db.String(50),
        nullable=False
    )

    lida = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    data = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        nullable=False
    )

    usuario = db.relationship(
        "Usuario",
        backref=db.backref(
            "notificacoes",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    denuncia = db.relationship(
        "Denuncia",
        backref=db.backref(
            "notificacoes",
            lazy=True
        )
    )

    def __repr__(self):
        return (
            f"<Notificacao "
            f"{self.id_notificacao} - "
            f"{self.titulo}>"
        )