
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Blueprint, flash, render_template, request, session, redirect
from flask_babel import gettext as _

from utils.images import save_image
from get_db import get_db
from login_required import login_required

new_post_bp = Blueprint('new_post', __name__)


@new_post_bp.route('/new_post')
@login_required
def new_post():
    return render_template("profile/blog/new_post.html")

@new_post_bp.route('/new_post', methods=["POST"])
@login_required
def send_post():
    title = request.form.get("title")
    text = request.form.get("description")

    if not title or not text:
        flash(_("The title and text are required fields"))
        return render_template("profile/blog/new_post.html")

    images = request.files.getlist("images")
    if len(images) > 3:
        flash(_("You can upload no more than 3 images"))
        return render_template("profile/blog/new_post.html")

    saved_images = []
    folder = f"uploads/posts/{session['username']}"
    os.makedirs(folder, exist_ok=True)

    def save_worker(file):
        return save_image(file, folder, prefix="post_image")

    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(save_worker, f) for f in images if f and f.filename]
            for future in as_completed(futures):
                saved_images.append(future.result())
    except ValueError:
        for path in saved_images:
            if os.path.exists(path):
                os.remove(path)
        flash(_("Please upload a valid image"))
        return render_template("profile/blog/new_post.html")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
        row = cursor.fetchone()
        if not row:
            session.clear()
            return redirect('/login')
        user_id = row[0]
        cursor.execute(
            "INSERT INTO blog_posts (user_id, title, content, created_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP) RETURNING id",
            (user_id, title, text)
        )
        post_id = cursor.fetchone()[0]

        for img_path in saved_images:
            cursor.execute(
                "INSERT INTO blog_post_images (post_id, image_path) VALUES (?, ?)",
                (post_id, img_path)
            )

        conn.commit() 
    return redirect(f"/blog/{user_id}")

