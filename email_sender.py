
import os
import secrets
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask_babel import gettext as _
from dotenv import load_dotenv

load_dotenv()

site_host = os.environ["SITE_HOST"]

sender_email = os.environ["SENDER_EMAIL"]
password = os.environ["SENDER_EMAIL_PASSWORD"]

smtp_host = os.environ["SMTP_HOST"]
smtp_port = os.environ["SMTP_PORT"]


def send_verification_code(receiver_email):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = _("Password recovery on {site_host}").format(site_host=site_host)
    code = f"{secrets.randbelow(1000000):06}"
    body = _("Hello,\n\nWe received a request to reset your password for your account on {site_host}.\n\nTo reset your password, please use the following code:\n\n{reset_code}\n\nIf you did not request this, please ignore this email.").format(site_host=site_host, reset_code=code)
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(sender_email, password)
            server.send_message(message)
        return code
    except Exception as e:
        logging.error(e, exc_info=True)
