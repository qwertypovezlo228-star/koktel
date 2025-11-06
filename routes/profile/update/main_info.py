
import os

from flask import Blueprint, request, redirect, session
from contextlib import suppress
from get_db import get_db
from login_required import login_required
from utils.images import save_image

main_bp = Blueprint('main', __name__)

@main_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    username = session['username']
    description = request.form.get('description', '')
    category = request.form.get('category', "0")
    if category not in ("0", "1", "2"):
        category = "0"
    city = request.form.get('city', '')
    if city not in [
        'Kyiv', 'Lviv', 'Kharkiv', 'Odesa', 'Dnipro',
        'Zaporizhzhia', 'Ivano-Frankivsk', 'Ternopil',
        'Chernivtsi', 'Uzhhorod', 'Poltava', 'Chernihiv',
        'Zhytomyr', 'Khmelnytskyi', 'Lutsk', 'Vinnytsia'
    ]:
        city = 'Kyiv'

    avatar_file = request.files.get('avatar')

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET description = ?, category = ?, city = ? 
            WHERE username = ?
        """, (description, category, city, username))

        if avatar_file and avatar_file.filename:
            with suppress(ValueError):
                avatar_path = save_image(
                    avatar_file, 
                    folder="uploads/avatars", 
                    prefix=f"{username}_avatar"
                )
                for pic in os.listdir("uploads/avatars"):
                    if pic.startswith(f"{username}_avatar") and pic != os.path.basename(avatar_path):
                        os.remove(os.path.join("uploads/avatars", pic))
                cursor.execute("UPDATE users SET avatar = ? WHERE username = ?", (avatar_path, username))

        conn.commit()

    return redirect(f"/profile/{username}")

