
from flask import Blueprint
from flask import redirect, url_for

from get_db import get_db
from login_required import admin_required

verification_bp = Blueprint('verification', __name__)

@verification_bp.route('/verify_user/<int:user_id>')
@admin_required
def verify_user(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_verified=1 WHERE id=?", (user_id,))
        conn.commit()
        return redirect(url_for('admin.admin_panel'))

@verification_bp.route('/unverify_user/<int:user_id>')
@admin_required
def unverify_user(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_verified=0 WHERE id=?", (user_id,))
        conn.commit()
        return redirect(url_for('admin.admin_panel'))


