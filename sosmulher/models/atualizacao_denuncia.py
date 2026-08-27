from sosmulher import db
class AtualizacaoDenuncia(db.Model):
    __tablename__ = "AtualizacaoDenuncia"

    id_atualizacao = db.Column(
        db.Integer,
        primary_key=True
    )

    id_denuncia = db.Column(
        db.Integer,
        db.ForeignKey("Denuncia.id_denuncia"),
        nullable=False
    )

    id_admin = db.Column(
        db.Integer,
        db.ForeignKey("Usuario.id_usuario"),
        nullable=False
    )

    mensagem = db.Column(
        db.Text,
        nullable=False
    )

    tipo = db.Column(
        db.String(30),
        default="atualizacao"
    )

    status_anterior = db.Column(
        db.String(30),
        nullable=True
    )

    status_novo = db.Column(
        db.String(30),
        nullable=True
    )

    data = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    lida = db.Column(
        db.Boolean,
        default=False
    )

    denuncia = db.relationship(
        "Denuncia",
        backref="atualizacoes"
    )

    admin = db.relationship(
        "Usuario"
    )