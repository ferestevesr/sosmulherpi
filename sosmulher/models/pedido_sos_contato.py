from sosmulher import db


class PedidoSOSContato(db.Model):

    __tablename__ = "PedidoSOSContato"

    id_sos_contato = db.Column(
        db.Integer,
        primary_key=True
    )

    id_sos = db.Column(
        db.Integer,
        db.ForeignKey("PedidoSOS.id_sos"),
        nullable=False
    )

    id_contato = db.Column(
        db.Integer,
        db.ForeignKey("ContatoEmergencia.id_contato"),
        nullable=False
    )

    contato = db.relationship(
        "ContatoEmergencia",
        backref=db.backref("pedidos_sos", lazy=True)
    )