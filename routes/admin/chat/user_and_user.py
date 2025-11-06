
from sqlite3 import Row
from flask import Blueprint, render_template

from get_db import get_db
from login_required import admin_required

user_and_user_bp = Blueprint('user_and_user', __name__)

@user_and_user_bp.route('/chat/<user1>/<user2>')
@admin_required
def admin_view_chat(user1, user2):
    with get_db() as conn:
        conn.row_factory = Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sender, content, media_urls, status, reply_to
            FROM messages
            WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
            ORDER BY id ASC
        """, (user1, user2, user2, user1))
        messages = cursor.fetchall()
    return render_template("admin/admin_view_chat.html", user1=user1, user2=user2, messages=messages)

@user_and_user_bp.route('/messages')
@admin_required
def view_messages():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT 
                CASE 
                    WHEN sender < receiver THEN sender 
                    ELSE receiver 
                END AS user1,
                CASE 
                    WHEN sender < receiver THEN receiver 
                    ELSE sender 
                END AS user2
            FROM messages
            WHERE sender != receiver
        """)
        dialogs = cursor.fetchall()

    return render_template("admin/messages.html", dialogs=dialogs)

