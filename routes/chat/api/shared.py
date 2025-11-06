
from datetime import datetime

from flask import Blueprint, request, session, jsonify
from get_db import get_db

shared_bp = Blueprint('shared', __name__)   


@shared_bp.route('/get_shared_messages')
def get_shared_messages():
    if not session.get('username'):
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.sender, m.text, m.media_urls, m.reply_to, u.avatar, m.timestamp
        FROM shared_messages m
        LEFT JOIN users u ON m.sender = u.username
        ORDER BY m.id ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    prev_sender = None
    temp_msgs = []

    for row in rows:
        sender = row[0]
        text = row[1]
        media_urls = row[2].split(',') if row[2] else []
        reply_to = row[3]
        avatar_url = row[4] if row[4] else "/static/images/Sample_User_Icon.png"
        if not avatar_url.startswith("/"):
            avatar_url = "/" + avatar_url
        raw_timestamp = row[5]

        timestamp_iso = None
        if raw_timestamp:
            dt = datetime.strptime(raw_timestamp, "%Y-%m-%d %H:%M:%S")
            timestamp_iso = dt.isoformat() + "Z"

        show_username = sender != prev_sender
        prev_sender = sender

        temp_msgs.append({
            "username": sender,
            "avatar_url": avatar_url,
            "message": text,
            "media_urls": media_urls,
            "reply_to": reply_to,
            "timestamp": timestamp_iso,
            "show_username": show_username,
        })

    for i, msg in enumerate(temp_msgs):
        is_last = (i == len(temp_msgs) - 1) or (temp_msgs[i+1]["username"] != msg["username"])
        msg["show_avatar"] = is_last

    return jsonify(temp_msgs)

 
@shared_bp.route('/send_shared_message', methods=['POST'])
def send_shared_message():
    if not session.get('username'):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    sender = session['username']
    message = data.get('message', '').strip()
    media_urls = data.get('media_urls', []) or []
    reply_to = data.get('reply_to', '')

    if not message and not media_urls:
        return jsonify({"error": "Empty message"}), 400

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO shared_messages (sender, text, media_urls, reply_to, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """, (sender, message, ','.join(media_urls) if media_urls else None, reply_to, timestamp))
        conn.commit()
    except Exception as e:
        return jsonify({"error": f"DB error: {str(e)}"}), 500
    finally:
        conn.close()

    return jsonify({"success": True, "timestamp": timestamp})


