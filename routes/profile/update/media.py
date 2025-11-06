
import os
import mimetypes

from flask import Blueprint
from flask import request, redirect, session
from werkzeug.utils import secure_filename

from login_required import login_required

ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska'
}

media_bp = Blueprint('media', __name__)

@media_bp.route('/upload_media', methods=['POST'])
@login_required
def upload_media():
    username = session['username']
    user_folder = os.path.join('uploads/media', username)
    os.makedirs(user_folder, exist_ok=True)

    uploaded_files = request.files.getlist('media_files')
    for file in uploaded_files:
        if file and file.filename:
            mimetype = file.mimetype
            if mimetype in ALLOWED_MIME_TYPES:
                filename = secure_filename(file.filename)
                file.save(os.path.join(user_folder, filename))

    return redirect(f"/profile/{username}")

@media_bp.route('/delete_photo', methods=['POST'])
@login_required
def delete_photo():
    username = session['username']
    filename = request.form.get('filename')
    if not filename:
        return "Файл не вказано", 400

    file_path = os.path.join('uploads/media', username, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect(f"/profile/{username}")

