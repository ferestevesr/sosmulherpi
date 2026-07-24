from sosmulher import db

class Localizacao(db.Model):

    __tablename__ = "Localizacao"
    
    id_localizacao = db.Column(db.Integer, primary_key=True)
    id_denuncia = db.Column(db.Integer, db.ForeignKey("Denuncia.id_denuncia"), nullable=False)
    cep = db.Column(db.String(9), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    

    def __repr__(self):
        return f"<Localizacao {self.id_localizacao} - {self.endereco}>"