

from flask import Blueprint
from routes.profile.update.main_info import main_bp
from routes.profile.update.media import media_bp
from routes.profile.update.products import products_bp

update_bp = Blueprint('update', __name__)

update_bp.register_blueprint(main_bp)
update_bp.register_blueprint(media_bp)
update_bp.register_blueprint(products_bp)
