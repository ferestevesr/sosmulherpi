from sosmulher import db

class Atendimento(db.Model):
    __tablename__ = "Atendimento"
    
    id_atendimento = db.Column(db.Integer, primary_key=True)
    id_denuncia = db.Column(db.Integer, db.ForeignKey("Denuncia.id_denuncia"), nullable=False)
    id_admin = db.Column(db.Integer, db.ForeignKey("Usuario.id_usuario"), nullable=False)
    data_inicio = db.Column(db.DateTime, default=db.func.current_timestamp())
    data_fim = db.Column(db.DateTime)
    descricao = db.Column(db.Text, nullable=False)
  