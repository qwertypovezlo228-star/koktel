
from flask import Blueprint
from flask import render_template

from get_db import get_db
from login_required import login_required

view_partners_bp = Blueprint('view_partners', __name__)

@view_partners_bp.route('/partners')
@login_required
def partners():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, cover, link, link_text FROM partners")
        partners = cursor.fetchall()
    return render_template("partners.html", partners=partners)

