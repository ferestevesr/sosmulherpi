import os

from werkzeug.utils import secure_filename

from sosmulher import db
from sosmulher.models.arquivo import Arquivo


def salvar_arquivo(arquivo, id_denuncia):

    if not arquivo:
        return None

    if not arquivo.filename:
        return None

    nome_arquivo = secure_filename(
        arquivo.filename
    )

    pasta_upload = os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)
        ),
        "static",
        "uploads"
    )

    os.makedirs(
        pasta_upload,
        exist_ok=True
    )

    caminho = os.path.join(
        pasta_upload,
        nome_arquivo
    )

    arquivo.save(caminho)

    extensao = nome_arquivo.rsplit(
        ".",
        1
    )[-1].lower()

    if extensao in [
        "jpg",
        "jpeg",
        "png"
    ]:

        tipo = "imagem"

    elif extensao == "mp4":

        tipo = "video"

    else:

        tipo = "documento"

    novo_arquivo = Arquivo(
        id_denuncia=id_denuncia,
        tipo=tipo,
        nome_arquivo=nome_arquivo
    )

    db.session.add(
        novo_arquivo
    )

    db.session.commit()

    return novo_arquivo