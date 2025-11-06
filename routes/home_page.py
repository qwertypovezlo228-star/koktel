
from flask import Blueprint, render_template, redirect, session
from login_required import login_required

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
@login_required
def index():
    return redirect('/home')

@home_bp.route('/home')
@login_required
def home():
    return render_template('home.html', username=session['username'])

