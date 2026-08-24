from sosmulher import db


class PedidoSOS(db.Model):

    __tablename__ = "PedidoSOS"

    id_sos = db.Column(
        db.Integer,
        primary_key=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("Usuario.id_usuario"),
        nullable=False
    )

    data_hora = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        nullable=False
    )

    latitude = db.Column(
        db.Float,
        nullable=False
    )

    longitude = db.Column(
        db.Float,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="em_andamento",
        nullable=False
    )

    usuario = db.relationship(
        "Usuario",
        backref=db.backref(
            "pedidos_sos",
            lazy=True
        )
    )

    contatos = db.relationship(
        "PedidoSOSContato",
        backref="pedido_sos",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<PedidoSOS {self.id_sos} - {self.status}>"