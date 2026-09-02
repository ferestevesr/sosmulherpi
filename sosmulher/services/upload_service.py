import os
from uuid import uuid4

from flask import current_app
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

    if not nome_arquivo or "." not in nome_arquivo:
        return None

    extensao = nome_arquivo.rsplit(
        ".",
        1
    )[-1].lower()

    extensoes_permitidas = {
        "jpg", "jpeg", "png", "mp4", "pdf", "doc", "docx"
    }

    if extensao not in extensoes_permitidas:
        return None

    if not conteudo_compativel(arquivo, extensao):
        return None

    # Impede que anexos com o mesmo nome sobrescrevam arquivos existentes.
    nome_arquivo = f"{uuid4().hex}.{extensao}"

    # Evidências não devem ser servidas publicamente pela pasta static.
    pasta_upload = os.path.join(current_app.instance_path, "uploads")

    os.makedirs(
        pasta_upload,
        exist_ok=True
    )

    caminho = os.path.join(
        pasta_upload,
        nome_arquivo
    )

    arquivo.save(caminho)

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


def conteudo_compativel(arquivo, extensao):
    """Faz uma verificação simples de assinatura antes de salvar o anexo."""
    assinaturas = {
        "jpg": (b"\xff\xd8\xff",),
        "jpeg": (b"\xff\xd8\xff",),
        "png": (b"\x89PNG\r\n\x1a\n",),
        "pdf": (b"%PDF-",),
        "doc": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
        "docx": (b"PK\x03\x04",),
    }

    inicio = arquivo.stream.read(16)
    arquivo.stream.seek(0)

    if extensao == "mp4":
        return len(inicio) >= 8 and inicio[4:8] == b"ftyp"

    return inicio.startswith(assinaturas[extensao])
