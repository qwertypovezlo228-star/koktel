
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Blueprint, flash, render_template, request, session, redirect
from flask_babel import gettext as _

from utils.images import save_image
from get_db import get_db
from login_required import login_required

edit_post_bp = Blueprint('edit_post', __name__)


@edit_post_bp.route('/edit_post/<int:post_id>')
@login_required
def edit_post(post_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
        row = cursor.fetchone()
        if not row:
            session.clear()
            return redirect('/login')
        user_id = row[0]

        cursor.execute(
            "SELECT id, title, content FROM blog_posts WHERE id = ? AND user_id = ?",
            (post_id, user_id)
        )
        post = cursor.fetchone()
        if not post:
            flash(_("Post not found"))
            return redirect(f"/blog/{user_id}")

        post_dict = {
            "id": post[0],
            "title": post[1],
            "content": post[2],
        }

        cursor.execute(
            "SELECT id, image_path FROM blog_post_images WHERE post_id = ?",
            (post_id,)
        )
        images = [{"id": r[0], "path": r[1]} for r in cursor.fetchall()]
        post_dict["images"] = images

    return render_template("profile/blog/edit_post.html", post=post_dict)


@edit_post_bp.route('/edit_post/<int:post_id>', methods=["POST"])
@login_required
def save_post(post_id):
    title = request.form.get("title")
    text = request.form.get("description")
    delete_images_ids = request.form.getlist("delete_images")

    if not title or not text:
        flash(_("The title and text are required fields"))
        return redirect(request.url)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
        row = cursor.fetchone()
        if not row:
            session.clear()
            return redirect('/login')
        user_id = row[0]

        cursor.execute(
            "SELECT id FROM blog_posts WHERE id = ? AND user_id = ?",
            (post_id, user_id)
        )
        if not cursor.fetchone():
            flash(_("Post not found"))
            return redirect(f"/blog/{user_id}")

        for img_id in delete_images_ids:
            cursor.execute("SELECT image_path FROM blog_post_images WHERE id = ? AND post_id = ?", (img_id, post_id))
            img_row = cursor.fetchone()
            if img_row:
                path = img_row[0]
                if os.path.exists(path):
                    os.remove(path)
                cursor.execute("DELETE FROM blog_post_images WHERE id = ?", (img_id,))

        images = request.files.getlist("images")
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
            return redirect(request.url)

        for img_path in saved_images:
            cursor.execute(
                "INSERT INTO blog_post_images (post_id, image_path) VALUES (?, ?)",
                (post_id, img_path)
            )

        cursor.execute(
            "UPDATE blog_posts SET title = ?, content = ? WHERE id = ?",
            (title, text, post_id)
        )

        conn.commit()

    return redirect(f"/blog/{user_id}")

