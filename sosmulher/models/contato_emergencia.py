from sosmulher import db

class ContatoEmergencia(db.Model):

    __tablename__ = "ContatoEmergencia"
    id_contato = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("Usuario.id_usuario"), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    parentesco = db.Column(db.String(50), nullable=False)