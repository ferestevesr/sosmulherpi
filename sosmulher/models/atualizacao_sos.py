from datetime import datetime

from sosmulher import db


class AtualizacaoSOS(db.Model):

    __tablename__ = "AtualizacaoSOS"

    id_atualizacao = db.Column(
        db.Integer,
        primary_key=True
    )

    id_sos = db.Column(
        db.Integer,
        db.ForeignKey("PedidoSOS.id_sos"),
        nullable=False
    )

    id_admin = db.Column(
        db.Integer,
        db.ForeignKey("Usuario.id_usuario"),
        nullable=True
    )

    mensagem = db.Column(
        db.Text,
        nullable=False
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
        default=datetime.now
    )

    lida = db.Column(
        db.Boolean,
        default=False
    )

    admin = db.relationship("Usuario")
