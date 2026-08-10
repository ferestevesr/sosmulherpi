from sosmulher import db


class Denuncia(db.Model):

    __tablename__ = "Denuncia"

    id_denuncia = db.Column(
        db.Integer,
        primary_key=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("Usuario.id_usuario"),
        nullable=False
    )

    titulo = db.Column(
        db.String(100),
        nullable=False
    )

    descricao = db.Column(
        db.Text,
        nullable=False
    )

    tipo = db.Column(
        db.Enum(
            "violencia_fisica",
            "violencia_psicologica",
            "violencia_sexual",
            "assedio",
            "ameaca",
            "outro"
        ),
        nullable=False
    )

    data = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    status = db.Column(
        db.Enum(
            "pendente",
            "em_andamento",
            "finalizado",
            "cancelado"
        ),
        default="pendente"
    )

    anonimo = db.Column(
        db.Boolean,
        default=False
    )

    nivel_risco = db.Column(
        db.Enum(
            "baixo",
            "medio",
            "alto",
            "emergencia"
        ),
        nullable=False
    )

    localizacao = db.relationship(
        "Localizacao",
        backref="denuncia",
        uselist=False,
        cascade="all, delete-orphan"
    )

    arquivos = db.relationship(
        "Arquivo",
        backref="denuncia",
        lazy=True,
        cascade="all, delete-orphan"
    )

    historicos = db.relationship(
        "Historico",
        backref="denuncia",
        lazy=True,
        cascade="all, delete-orphan"
    )

    atendimento = db.relationship(
        "Atendimento",
        backref="denuncia",
        lazy=True,
        cascade="all, delete-orphan"
    )