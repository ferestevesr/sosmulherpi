import smtplib

from email.message import EmailMessage

from flask import current_app


def enviar_email(
    destinatario,
    assunto,
    mensagem
):

    servidor = current_app.config.get(
        "MAIL_SERVER"
    )

    porta = current_app.config.get(
        "MAIL_PORT"
    )

    usuario = current_app.config.get(
        "MAIL_USERNAME"
    )

    senha = current_app.config.get(
        "MAIL_PASSWORD"
    )

    remetente = current_app.config.get(
        "MAIL_DEFAULT_SENDER"
    )


    if not usuario or not senha:

        raise RuntimeError(
            "Configuração de e-mail não encontrada."
        )


    email = EmailMessage()

    email["Subject"] = assunto
    email["From"] = remetente
    email["To"] = destinatario

    email.set_content(
        mensagem
    )


    with smtplib.SMTP(
        servidor,
        porta
    ) as smtp:

        smtp.starttls()

        smtp.login(
            usuario,
            senha
        )

        smtp.send_message(
            email
        )