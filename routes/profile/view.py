
import os

from flask import Blueprint
from flask import render_template, redirect, session, url_for

from get_db import get_db
from login_required import login_required

view_bp = Blueprint('view', __name__)

@view_bp.route('/')
@login_required
def my_profile():
    return redirect(f"/profile/{session['username']}")

@view_bp.route('/<int:user_id>')
@login_required
def profile_by_id(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return render_template('profile/404.html'), 404
        username = user[1]
    return redirect(url_for("profile.view.profile", username=username))

@view_bp.route('/<username>')
@login_required
def profile(username):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        if not user:
            return render_template('profile/404.html'), 404
        if session['username'] not in (username, "admin") and user[7] in (0, None):
            return render_template('profile/404.html'), 404
        user_id = user[0]
        cursor.execute("SELECT id, title, description, price, image_filename, currency FROM products WHERE user_id=?", (user_id,))
        products = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM messages WHERE receiver=? AND is_read=0", (session['username'],))
        unread_count = cursor.fetchone()[0]
        cursor.execute(
            "SELECT 1 FROM blog_subscriptions WHERE subscriber_id = (SELECT id FROM users WHERE username = ?) AND model_id = ?",
            (session["username"], user_id)
        )
        is_subscribed = cursor.fetchone() is not None
    user_folder = os.path.join('uploads/media', username)
    photos = os.listdir(user_folder) if os.path.exists(user_folder) else []
    if session["username"] == username:
        return render_template('profile/edit.html', user=user, username=username, photos=photos, products=products, unread_count=unread_count)
    else:
        return render_template('profile/view.html', user=user, username=username, photos=photos, products=products, unread_count=unread_count, is_subscribed=is_subscribed)

