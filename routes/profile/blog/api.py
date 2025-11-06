
import sqlite3

from flask import Blueprint, render_template, request, session, redirect
from flask_babel import gettext as _

from get_db import get_db
from login_required import login_required

blog_api_bp = Blueprint('blog_api', __name__)


@blog_api_bp.route('/api/subscribe/<int:user_id>')
@login_required
def subscribe_to_user(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (session["username"],))
        id = cursor.fetchone()
        if id:
            id = id[0]
            cursor.execute("INSERT OR IGNORE INTO blog_subscriptions (subscriber_id, model_id) VALUES (?, ?)", (id, user_id))
            conn.commit()
            return "OK"
    return "FAIL"

@blog_api_bp.route('/api/unsubscribe/<int:user_id>')
@login_required
def unsubscribe_to_user(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (session["username"],))
        id = cursor.fetchone()
        if id:
            id = id[0]
            cursor.execute("DELETE FROM blog_subscriptions WHERE subscriber_id = ? AND model_id = ?", (id, user_id))
            conn.commit()
            return "OK"
    return "FAIL"

@blog_api_bp.route('/api/get_news_cards/')
@login_required
def get_news_cards():
    subscribes_only = request.args.get("subscribes") == "1"
    filter_user_id = request.args.get("user_id", type=int)
    current_user_id = None

    username = session.get('username')
    is_admin = username == 'admin'

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, category FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            current_user_id = row[0]
            current_category = row[1] if row[1] is not None else 0
        else:
            session.clear()
            return redirect("/login")

    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        base_query = """
            SELECT 
                p.id,
                p.user_id,
                p.title,
                p.content,
                strftime('%Y-%m-%d %H:%M', p.created_at) AS created_at,
                u.username,
                u.avatar,
                u.name,
                CASE 
                    WHEN s.subscriber_id IS NOT NULL THEN 1
                    ELSE 0
                END AS is_subscribed,
                GROUP_CONCAT(i.image_path, ',') AS images
            FROM blog_posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN blog_subscriptions s 
                ON s.subscriber_id = ? AND s.model_id = p.user_id
            LEFT JOIN blog_post_images i
                ON i.post_id = p.id
        """

        conditions = []
        params = [current_user_id]

        if subscribes_only:
            conditions.append("s.subscriber_id IS NOT NULL")

        if filter_user_id:
            next_page = f"/blog/{filter_user_id}"
            conditions.append("p.user_id = ?")
            params.append(filter_user_id)
        else:
            next_page = "/blog"

        if not is_admin:
            conditions.append("(p.user_id = ? OR u.category != 0)")
            params.append(current_user_id)

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += """
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """

        cursor.execute(base_query, tuple(params))
        posts = []
        for row in cursor.fetchall():
            post = dict(row)
            post["images"] = post["images"].split(",") if post["images"] else []
            posts.append(post)

    return render_template("profile/blog/news_cards.html", posts=posts, next=next_page)

