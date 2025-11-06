
import os
import uuid
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file, folder: str, prefix: str) -> str:
    if not file or not file.filename:
        raise ValueError("No file provided")

    if not allowed_file(file.filename):
        raise ValueError("Invalid file type")

    try:
        img = Image.open(file)
        img.load()
    except UnidentifiedImageError:
        raise ValueError("Uploaded file is not a valid image")

    os.makedirs(folder, exist_ok=True)

    filename = f"{prefix}_{uuid.uuid4().hex}.png"
    filepath = os.path.join(folder, secure_filename(filename))

    img = img.convert("RGBA")
    img.save(filepath, format="PNG")

    return filepath

