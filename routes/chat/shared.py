
from flask import Blueprint, render_template, session
from login_required import login_required

shared_bp = Blueprint('shared', __name__)

@shared_bp.route('/shared_chat')
@login_required
def shared_chat():
    return render_template('chat/shared_chat.html', username=session['username'])


