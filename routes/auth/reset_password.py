
from contextlib import suppress
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_babel import gettext as _
from email_validator import validate_email, EmailUndeliverableError, EmailSyntaxError

from get_db import get_db
from email_sender import send_verification_code
from routes.auth.add_user import is_valid_password

reset_password_bp = Blueprint('reset_password', __name__)

def clear_reset_stage():
    with suppress(KeyError):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM password_reset_codes WHERE email = ?', (session['reset_email'],))
            conn.commit()
    session.pop('reset_email', None)
    session.pop('reset_stage', None)


def enter_email():
    email = request.form.get('email')
    if not email:
        return render_template('auth/reset_password/enter_email.html')

    try:
        validate_email(email)
    except (EmailUndeliverableError, EmailSyntaxError):
        flash(_("Invalid email"))
        return render_template('auth/reset_password/enter_email.html')

    with get_db() as conn:
        cursor = conn.cursor()
        user = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

    if not user:
        flash(_('There is no user with this email address'))
        return render_template('auth/reset_password/enter_email.html')

    reset_code = send_verification_code(email)
    if reset_code is not None:
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM password_reset_codes WHERE email = ?
            """, (email,))
            cursor.execute("""
                INSERT INTO password_reset_codes (email, code, expires_at)
                VALUES (?, ?, ?)
            """, (email, reset_code, expires_at))
            conn.commit()
        session['reset_email'] = email.strip()
        session['reset_stage'] = 'verify'
        return redirect(url_for('reset_password.reset_password'))

def verify():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM password_reset_codes WHERE expires_at < CURRENT_TIMESTAMP")
        conn.commit()

    code = request.form.get('code')

    with get_db() as conn:
        cursor = conn.cursor()

        result = cursor.execute("""
            SELECT * FROM password_reset_codes
            WHERE email = ? AND code = ? AND expires_at > CURRENT_TIMESTAMP
        """, (session['reset_email'], code)).fetchone()

    if not result:
        flash(_('Invalid code'))
        return render_template('auth/reset_password/verify.html', email=session['reset_email'])

    session['reset_stage'] = 'enter_password'
    return redirect(url_for('reset_password.reset_password'))

def enter_password():
    error_msg = None

    password = request.form.get('password')
    confirm = request.form.get('password_confirm')

    if not password or password != confirm:
        error_msg = _('The passwords do not match')

    if not is_valid_password(password):
        error_msg = _('Invalid password')

    if error_msg is not None:
        flash(error_msg)
        return render_template('auth/reset_password/enter_password.html')

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET password = ? WHERE email = ?', (password, session['reset_email']))
        conn.commit()

    flash(_('Password successfully updated, you can now log in to your account'))
    clear_reset_stage()
    return redirect(url_for('auth.login'))

@reset_password_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    stage = session.get('reset_stage', 'enter_email')

    if request.method == 'POST':
        if stage == 'enter_email':
            return enter_email()

        elif stage == 'verify':
            return verify()

        elif stage == 'enter_password':
            return enter_password()

    if stage == 'verify':
        return render_template('auth/reset_password/verify.html', email=session['reset_email'])
    elif stage == 'enter_password':
        return render_template('auth/reset_password/enter_password.html')
    else:
        session['reset_stage'] = 'enter_email'
        return render_template('auth/reset_password/enter_email.html')

@reset_password_bp.route('/reset-password/change-email')
def change_email():
    clear_reset_stage()
    return redirect(url_for('reset_password.reset_password'))
