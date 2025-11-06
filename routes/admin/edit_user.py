from os import remove
from contextlib import suppress
from shutil import rmtree

from flask import Blueprint
from flask import render_template, request, redirect, url_for

from get_db import get_db
from login_required import admin_required
from routes.auth.add_user import add_user

edit_user_bp = Blueprint('edit_user', __name__)

@edit_user_bp.route('/add_user', methods=['GET', 'POST'])
@admin_required
def add_user_from_admin_panel():
    if request.method == 'POST':
        username = request.form['username'].lower().strip()
        email = request.form['email'].lower().strip()
        password = request.form['password']
        name = request.form['name']
        result = add_user(username, email, password, name)
        if result["success"]:
            return redirect('/admin')
        else:
            return render_template('admin/add_user.html', error=result["error"])
    return render_template('admin/add_user.html')

@edit_user_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            name = request.form['name']
            password = request.form['password']
            cursor.execute("UPDATE users SET name = ?, password = ? WHERE id = ?", (name, password, user_id))
            conn.commit()
            return redirect('/admin')

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

    return render_template('admin/edit_user.html', user=user)

@edit_user_bp.route('/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id=?", (user_id,))
        username = cursor.fetchone()
        cursor.execute("DELETE FROM blog_post_images WHERE post_id IN (SELECT id FROM blog_posts WHERE user_id=?)", (user_id,))
        cursor.execute("DELETE FROM blog_posts WHERE user_id=?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        cursor.execute("DELETE FROM products WHERE user_id=?", (user_id,))
        conn.commit()

    if username:
        username = username[0]
        for f in ("media", "products", "posts"):
            with suppress(FileNotFoundError):
                rmtree(f"uploads/{f}/{username}")
        with suppress(FileNotFoundError):
            remove(f"uploads/avatars/{username}_avatar.png")

    return redirect(url_for('admin.admin_panel'))

