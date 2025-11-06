
from flask import Blueprint

from routes.chat.api import api_bp
from routes.chat.shared import shared_bp
from routes.chat.dialogs_list import dialogs_bp
from routes.chat.p2p import p2p_bp

chat_bp = Blueprint('chat', __name__)

chat_bp.register_blueprint(api_bp)
chat_bp.register_blueprint(shared_bp)
chat_bp.register_blueprint(dialogs_bp)
chat_bp.register_blueprint(p2p_bp)
