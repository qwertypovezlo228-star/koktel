
from functools import wraps
from flask import redirect, session, render_template

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect("/login")
        return func(*args, **kwargs)
    return decorated_function

def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get('username') != 'admin':
            return render_template("404.html")
        return func(*args, **kwargs)
    return decorated_function
