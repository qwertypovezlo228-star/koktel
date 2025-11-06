
import re
from flask_babel import gettext as _
from email_validator import validate_email, EmailUndeliverableError, EmailSyntaxError

from get_db import get_db

USERNAME_REGEX = re.compile(r'^[a-z0-9](?:[a-z0-9_]{1,28}[a-z0-9])?$')

def is_valid_username(username):
    if not(3 <= len(username) <= 30):
        return False
    return bool(USERNAME_REGEX.fullmatch(username)) and username[0].isalpha()

def is_valid_password(password):
    if not (8 <= len(password) <= 64):
        return False
    if not re.search(r'[a-zA-Z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

def add_user(username, email, password, name):
    error_msg = None

    if name == "":
        error_msg = _("The name cannot be empty")

    try:
        validate_email(email)
    except (EmailUndeliverableError, EmailSyntaxError):
        error_msg = _("Invalid email")

    if not is_valid_username(username):
        error_msg = _("Invalid username")

    if not is_valid_password(password):
        error_msg = _("Invalid password")

    if error_msg is not None:
        return dict(success=False, error=error_msg)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            error_msg = _("A user with this login already exists.")
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        if cursor.fetchone():
            error_msg = _("A user with this email already exists.")

        if error_msg is not None: 
            return dict(success=False, error=error_msg)
        cursor.execute("INSERT INTO users (username, password, name, email, is_verified) VALUES (?, ?, ?, ?, ?)",
                       (username, password, name, email, 0))
        conn.commit()
        return dict(success=True, error=None)
