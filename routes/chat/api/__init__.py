
from flask import Blueprint

from routes.chat.api.p2p import p2p_bp
from routes.chat.api.upload_media import upload_media_bp
from routes.chat.api.get_dialogs import dialogs_bp
from routes.chat.api.shared import shared_bp

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(p2p_bp)
api_bp.register_blueprint(upload_media_bp)
api_bp.register_blueprint(dialogs_bp)
api_bp.register_blueprint(shared_bp)

