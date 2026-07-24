from sosmulher import db

class Historico(db.Model):

    __tablename__ = "Historico"

    id_historico = db.Column(db.Integer, primary_key=True)
    id_denuncia = db.Column(db.Integer, db.ForeignKey("Denuncia.id_denuncia"), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("Usuario.id_usuario"), nullable=False)
    acao = db.Column(db.String(255), nullable=False)
    observacao = db.Column(db.Text)
    data = db.Column(db.DateTime, default=db.func.current_timestamp())