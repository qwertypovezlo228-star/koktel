
import sqlite3

from flask import Blueprint, render_template, session, redirect
from flask_babel import gettext as _

from get_db import get_db
from login_required import login_required

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/blog')
@login_required
def blog():
    return render_template("profile/blog/main.html")

@posts_bp.route('/blog/<int:user_id>')
@login_required
def user_blog(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE id = ?", (user_id, ))
        name = cursor.fetchone()[0]
    return render_template("profile/blog/user.html", user_id=user_id, name=name)

@posts_bp.route('/blog_post/<int:post_id>')
@login_required
def blog_post(post_id):
    current_user_id = None
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
        row = cursor.fetchone()
        if row:
            current_user_id = row[0]
        else:
            session.clear()
            return redirect("/login")

    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT 
                p.id,
                p.user_id,
                p.title,
                p.content,
                strftime('%Y-%m-%d %H:%M', p.created_at) AS created_at,
                u.username,
                u.avatar,
                u.name,
                u.category,
                CASE 
                    WHEN s.subscriber_id IS NOT NULL THEN 1
                    ELSE 0
                END AS is_subscribed,
                GROUP_CONCAT(i.image_path, ',' ORDER BY i.id) AS images
            FROM blog_posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN blog_subscriptions s 
                ON s.subscriber_id = ? AND s.model_id = p.user_id
            LEFT JOIN blog_post_images i
                ON i.post_id = p.id
            WHERE p.id = ?
            GROUP BY p.id
        """

        cursor.execute(query, (current_user_id, post_id))
        row = cursor.fetchone()

        if not row:
            return _('Post not found'), 404
        
        post = dict(row)
        post["images"] = post["images"].split(",") if post["images"] else []

        if post["category"] == 0:
            if not (
                session["username"] == "admin" or post["user_id"] == current_user_id
            ):
                return _('Post not found'), 404

    return render_template("profile/blog/post.html", post=post)

