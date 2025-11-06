
import os
from contextlib import suppress

from flask import Blueprint, session, redirect, request
from flask_babel import gettext as _

from get_db import get_db
from login_required import login_required

delete_post_bp = Blueprint('delete_post', __name__)

@delete_post_bp.route('/delete_post/<int:id>')
@login_required
def delete_post(id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id=(SELECT user_id FROM blog_posts WHERE id = ?)", (id,))
        username = cursor.fetchone()
        if username:
            username = username[0]
            if username == session["username"]:
                cursor.execute("SELECT image_path FROM blog_post_images WHERE post_id = ?", (id,))
                image_paths = cursor.fetchall()
                for image_path in image_paths:
                    with suppress(FileNotFoundError):
                        os.remove(image_path[0])
                cursor.execute("DELETE FROM blog_post_images WHERE post_id = ?", (id,))
                cursor.execute("DELETE FROM blog_posts WHERE id = ?", (id,))
                conn.commit()

        next_page = request.args.get("next")
    return redirect(next_page or "/blog")


