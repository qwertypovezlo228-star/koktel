
from flask import Blueprint, render_template
from login_required import login_required

dialogs_bp = Blueprint('dialogs', __name__)

@dialogs_bp.route('/messages')
@login_required
def my_dialogs():
    return render_template('chat/my_dialogs.html')

