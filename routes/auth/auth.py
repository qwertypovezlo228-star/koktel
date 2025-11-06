
from flask import Blueprint, render_template, request, redirect, session
from flask_babel import gettext as _
from .add_user import add_user
from .reset_password import clear_reset_stage

from get_db import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'GET':
        error_param = request.args.get('error')
        if error_param == 'google_auth_error':
            error = _('Google authentication error. Please try again.')
        elif error_param == 'google_auth_failed':
            error = _('Google authentication failed. Please try again.')
    
    if request.method == 'POST':
        username = request.form['username'].lower().strip()
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            clear_reset_stage()
            session['username'] = username
            return redirect('/home')
        else:
            error = _('Invalid username or password')

    return render_template('auth/login.html', error=error, request=request)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].lower().strip()
        email = request.form['email'].lower().strip()
        password = request.form['password']
        name = request.form['name'].strip()
        result = add_user(username, email, password, name)
        if not result["success"]:
            return render_template('auth/register.html', error=result["error"])
        clear_reset_stage()
        return render_template('auth/register.html', success=_('Account created! Please log in now.')) 
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
