
from flask import Blueprint, render_template, request, flash
from flask_babel import gettext as _

from get_db import get_db

help_bp = Blueprint('help', __name__)

@help_bp.route('/help')
def help():
    return render_template('help.html')

@help_bp.route('/help', methods=["POST"])
def send_mail():
    contact = request.form.get("contact", None)
    message = request.form.get("message", None)
    if not contact or not message:
        flash(_("Both fields are required"))
    else:
        flash(_("Your message has been successfully sent"))
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO support_messages (contact, message)
                VALUES (?, ?)
                """,
                (contact, message)
            )
            conn.commit()
    return render_template('help.html')

