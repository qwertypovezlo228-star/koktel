
from flask import Blueprint, render_template, redirect, session, url_for

from get_db import get_db
from login_required import admin_required

shared_bp = Blueprint('shared', __name__)

@shared_bp.route('/shared_chat')
@admin_required
def shared_chat():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, sender, text, reply_to, media_urls FROM shared_messages ORDER BY timestamp ASC")
        messages = [{"id": row[0], "sender": row[1], "text": row[2], "reply_to": row[3], "media_urls": row[4]} for row in cursor.fetchall()]
    return render_template("admin/shared_chat.html", username=session['username'], messages=messages)

@shared_bp.route('/delete_shared_message/<int:msg_id>')
@admin_required
def delete_shared_message(msg_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shared_messages WHERE id=?", (msg_id,))
        conn.commit()
    return redirect(url_for('admin.shared.shared_chat'))

