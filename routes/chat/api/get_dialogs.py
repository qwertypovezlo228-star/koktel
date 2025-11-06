
from flask import Blueprint, session, jsonify
from get_db import get_db

dialogs_bp = Blueprint('dialogs', __name__)


@dialogs_bp.route("/get_dialogs")
def get_dialogs():
    if not session.get('username'):
        return jsonify({"error": "Unauthorized"}), 401

    current_user = session["username"]
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sender, receiver, MAX(timestamp) as last_time,
               SUM(CASE WHEN receiver = ? AND is_read = 0 THEN 1 ELSE 0 END) as unread_count
        FROM messages
        WHERE sender = ? OR receiver = ?
        GROUP BY 
            CASE
                WHEN sender < receiver THEN sender || '_' || receiver
                ELSE receiver || '_' || sender
            END
        ORDER BY 
            unread_count DESC,
            last_time DESC
    """, (current_user, current_user, current_user))

    dialogs = []
    for row in cursor.fetchall():
        sender, receiver, last_time, unread = row
        other_user = receiver if sender == current_user else sender

        # Получаем аватар
        cursor.execute("SELECT avatar FROM users WHERE username = ?", (other_user,))
        avatar_url = cursor.fetchone()
        dialogs.append({
            "username": other_user,
            "avatar": avatar_url,
            "unread": unread,
            "last_time": last_time
        })

    conn.close()
    return jsonify(dialogs)

