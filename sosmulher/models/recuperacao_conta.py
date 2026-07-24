from sosmulher import db

class RecuperacaoConta(db.Model):
    __tablename__ = "RecuperacaoConta"
    id_recuperacao = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("Usuario.id_usuario"), nullable=False)
    codigo = db.Column(db.String(100), nullable=False)
    data_expiracao = db.Column(db.DateTime, nullable=False)
    utilizado = db.Column(db.Boolean, default=False, nullable=False)