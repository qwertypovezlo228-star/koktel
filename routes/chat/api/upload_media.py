
import os

from flask import Blueprint, request, session, jsonify
from werkzeug.utils import secure_filename


upload_media_bp = Blueprint('upload_media', __name__)

@upload_media_bp.route('/upload_media_chat', methods=['POST'])
def upload_media_chat():
    if not session.get('username'):
        return jsonify({"error": "Unauthorized"}), 401
    uploaded_files = request.files.getlist("files[]")
    urls = []
    username = session['username']
    folder = os.path.join("uploads", "chat_uploads", username)
    os.makedirs(folder, exist_ok=True)
    for file in uploaded_files:
        filename = secure_filename(file.filename)
        path = os.path.join(folder, filename)
        file.save(path)
        urls.append(f"/{path}")
    return jsonify({"urls": urls})

