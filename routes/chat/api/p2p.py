
from datetime import datetime
from flask import Blueprint, request, session, jsonify
from get_db import get_db

p2p_bp = Blueprint('peer_to_peer', __name__)


@p2p_bp.route('/send_message', methods=['POST'])
def send_message():
    data = request.json

    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid JSON data'}), 400

    if not session.get('username'):
        return jsonify({"error": "Unauthorized"}), 401

    sender = session.get('username')
    receiver = data.get('receiver')
    message = data.get('message', '').strip()
    media_urls = data.get('media_urls', []) or []
    reply_to = data.get('reply')
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    if not sender or not receiver or (not message and not media_urls):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (sender, receiver, content, media_urls, status, reply, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            sender,
            receiver,
            message,
            ','.join(media_urls) if media_urls else None,
            'delivered',
            reply_to,
            timestamp
        ))
        conn.commit()
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

    return jsonify({
        'username': sender,
        'message': message,
        'media_urls': media_urls,
        'reply': reply_to,
        'timestamp': timestamp
    }), 200
    
@p2p_bp.route("/mark_seen", methods=["POST"])
def mark_seen():
    data = request.get_json()
    message_ids = data.get("message_ids", [])
    username = session.get("username")

    if not username or not message_ids:
        return jsonify({"status": "error"})

    conn = get_db()
    cursor = conn.cursor()

    query = f"""
        UPDATE messages
        SET is_read = 1
        WHERE id IN ({','.join(['?'] * len(message_ids))}) AND receiver = ?
    """
    cursor.execute(query, (*message_ids, username))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})
    

@p2p_bp.route("/get_messages")
def get_messages():
    username = request.args.get("username")
    sender = session.get("username")
    if not username or not sender:
        return jsonify([])

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.id, m.sender, m.content, m.media_urls, m.is_read, m.reply, m.timestamp, u.avatar
        FROM messages m
        LEFT JOIN users u ON m.sender = u.username
        WHERE (m.sender = ? AND m.receiver = ?) OR (m.sender = ? AND m.receiver = ?)
        ORDER BY m.id ASC
    """, (sender, username, username, sender))
    
    rows = cursor.fetchall()
    conn.close()

    messages = []
    prev_sender = None

    for i, row in enumerate(rows):
        msg_id, msg_sender, content, media, is_read, reply, timestamp, avatar = row
        avatar_url = avatar or "/static/images/Sample_User_Icon.png"
        if not avatar_url.startswith("/"):
            avatar_url = "/" + avatar_url

        show_username = msg_sender != prev_sender

        next_sender = rows[i + 1][1] if i + 1 < len(rows) else None
        show_avatar = (next_sender != msg_sender)

        messages.append({
            "id": msg_id,
            "username": msg_sender,
            "message": content,
            "media_urls": media.split(",") if media else [],
            "is_read": is_read,
            "reply": reply,
            "timestamp": timestamp,
            "avatar_url": avatar_url,
            "show_username": show_username,
            "show_avatar": show_avatar
        })

        prev_sender = msg_sender

    return jsonify(messages)

