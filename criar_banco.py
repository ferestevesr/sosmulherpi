from sosmulher import app, db

# Importa os modelos para o SQLAlchemy conhecer as tabelas
from sosmulher.models.usuario import Usuario
from sosmulher.models.denuncia import Denuncia
from sosmulher.models.pedido_sos import PedidoSOS
from sosmulher.models.pedido_sos_contato import PedidoSOSContato
from sosmulher.models.contato_emergencia import ContatoEmergencia

with app.app_context():
    db.create_all()
    print("Banco criado com sucesso!")