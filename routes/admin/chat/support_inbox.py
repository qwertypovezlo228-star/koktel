
from datetime import datetime

from flask import Blueprint
from flask import render_template, jsonify

from get_db import get_db
from login_required import admin_required

support_inbox_bp = Blueprint('support_inbox', __name__)


@support_inbox_bp.route("/api/get_support_messages")
@admin_required
def get_support_messages():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, contact, message, is_read, created_at
            FROM support_messages
            ORDER BY is_read DESC, created_at DESC
        """)

        messages_list = []
        for row in cursor.fetchall():
            id, contact, message, unread, created_at = row
            messages_list.append({
                "id": id,
                "contact": contact,
                "unread": 0 if unread else 1,
                "last_time": created_at,
                "last_message": message
            })
    return jsonify(messages_list)

@support_inbox_bp.route("/support_inbox")
@admin_required
def support_inbox():
    return render_template("admin/support_inbox.html")

@support_inbox_bp.route("/support_message/<int:id>")
@admin_required
def support_message(id):
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE support_messages
            SET is_read = 1
            WHERE id = ?
        """, (id,))
        conn.commit()

        cursor.execute("""
            SELECT contact, message, created_at
            FROM support_messages
            WHERE id = ?
        """, (id,))
        row = cursor.fetchone()

        if not row:
            return "Message not found", 404

        contact, message, created_at_str = row
        created_at = None
        if created_at_str:
            created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")

    return render_template(
        "admin/support_message.html",
        contact=contact,
        message=message,
        created_at=created_at
    )
