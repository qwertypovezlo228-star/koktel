
from flask import Blueprint, render_template

from routes.admin.edit_user import edit_user_bp
from routes.admin.edit_partner import edit_partner_bp
from routes.admin.verification import verification_bp
from routes.admin.chat.user_and_user import user_and_user_bp
from routes.admin.chat.shared import shared_bp
from routes.admin.chat.support_inbox import support_inbox_bp

from get_db import get_db
from login_required import admin_required

admin_bp = Blueprint('admin', __name__)
admin_bp.register_blueprint(edit_user_bp)
admin_bp.register_blueprint(edit_partner_bp)
admin_bp.register_blueprint(support_inbox_bp)
admin_bp.register_blueprint(verification_bp)
admin_bp.register_blueprint(user_and_user_bp)
admin_bp.register_blueprint(shared_bp)

@admin_bp.route('/')
@admin_required
def admin_panel():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, username, email, is_verified, ROW_NUMBER() OVER () AS row_num FROM users")
        users = cursor.fetchall()
    return render_template('admin/users_list.html', users=users)

@admin_bp.route('/partners')
@admin_required
def partners():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, link, ROW_NUMBER() OVER () AS row_num, link_text FROM partners")
        partners = cursor.fetchall()
    return render_template('admin/partners_list.html', partners=partners)



