from sosmulher import db


class Arquivo(db.Model):

    __tablename__ = "Arquivo"

    id_arquivo = db.Column(
        db.Integer,
        primary_key=True
    )

    id_denuncia = db.Column(
        db.Integer,
        db.ForeignKey("Denuncia.id_denuncia"),
        nullable=False
    )

    tipo = db.Column(
        db.Enum(
            "imagem",
            "video",
            "documento"
        ),
        nullable=False
    )

    nome_arquivo = db.Column(
        db.String(255),
        nullable=False
    )

    data_envio = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )