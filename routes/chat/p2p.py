
from flask import Blueprint, redirect, render_template, session
from get_db import get_db
from login_required import login_required

p2p_bp = Blueprint('peer_to_peer', __name__) 

@p2p_bp.route('/chat_with/<username>', methods=['GET', 'POST'])
@login_required
def chat_with(username):
    if username == session['username']:
        return redirect('/profile')

    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return render_template("profile/404.html"), 404

        cursor.execute("""
            SELECT sender, content, media_urls, status, reply
            FROM messages
            WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
            ORDER BY id ASC
        """, (session['username'], username, username, session['username']))
        messages = cursor.fetchall()

    room = "_".join(sorted([session['username'], username]))

    return render_template(
        "chat/private_chat.html",
        username=username,
        my_username=session['username'],
        messages=messages,
        room=room
    )

