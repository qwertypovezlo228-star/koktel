
import os
from datetime import datetime, timedelta

from flask import Flask, session, send_from_directory, render_template, redirect, request
from flask_babel import Babel, gettext as _, get_locale
from dotenv import load_dotenv

from get_db import get_db, create_db_if_not_exists
from routes import register_bp
from login_required import login_required

load_dotenv()

app = Flask(__name__)

create_db_if_not_exists()

app.secret_key = os.environ["SECRET_KEY"]
app.permanent_session_lifetime = timedelta(days=7)

# Налаштування сесій для Render (HTTPS)
app.config['SESSION_COOKIE_SECURE'] = True  # Для HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Захист від CSRF
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Захист від XSS

app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

register_bp(app)

def locale_selector():
    locale = session.get("locale")
    if locale is not None:
        return locale
    return request.accept_languages.best_match(['uk', 'ru', 'en'])

@app.before_request
def update_last_seen():
    # Пропускаємо перевірку для OAuth маршрутів
    if request.path.startswith('/login/google') or request.path.startswith('/login/apple'):
        return
    
    session.permanent = True
    if "username" in session:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE username = ?", (session["username"],))
            user = c.fetchone()
            if user:
                c.execute("UPDATE users SET last_seen = ? WHERE username = ?",
                          (datetime.utcnow().isoformat(), session["username"]))
                conn.commit()
            else:
                session.clear()
                return redirect('/login')

@app.context_processor
def inject_globals():
    return {
        'locale': get_locale(),
        '_': _
    }

@app.errorhandler(404)
@login_required
def page_not_found(_):
    return render_template('404.html'), 404

@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    session['locale'] = lang_code
    return redirect(request.referrer or url_for('home'))

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory('uploads', filename)

babel = Babel(app, locale_selector=locale_selector)

