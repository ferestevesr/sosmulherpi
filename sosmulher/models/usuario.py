from sosmulher import db
from flask_login import UserMixin


class Usuario(db.Model, UserMixin):

    __tablename__ = "Usuario"

    id_usuario = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    senha = db.Column(
        db.String(255),
        nullable=False
    )

    cpf = db.Column(
        db.String(14)
    )

    telefone = db.Column(
        db.String(20)
    )

    tipo = db.Column(
        db.Enum(
            "user",
            "admin",
            name="usuario_tipo_enum"
        ),
        default="user",
        nullable=False
    )

    status_conta = db.Column(
        db.Enum(
            "ativa",
            "bloqueada",
            "desativada",
            name="usuario_status_conta_enum"
        ),
        default="ativa",
        nullable=False
    )

    aceitou_termos = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    data_aceite_termos = db.Column(
        db.DateTime,
        nullable=True
    )

    denuncias = db.relationship(
        "Denuncia",
        backref="usuario",
        lazy=True,
        cascade="all, delete-orphan"
    )

    contato_emergencia = db.relationship(
        "ContatoEmergencia",
        backref="usuario",
        lazy=True,
        cascade="all, delete-orphan"
    )

    recuperacao_conta = db.relationship(
        "RecuperacaoConta",
        backref="usuario",
        lazy=True,
        cascade="all, delete-orphan"
    )

    atendimentos = db.relationship(
        "Atendimento",
        backref="usuario",
        lazy=True,
        cascade="all, delete-orphan"
    )

    historico = db.relationship(
        "Historico",
        backref="usuario",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def get_id(self):
        return str(self.id_usuario)