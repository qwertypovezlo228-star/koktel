
from flask import Blueprint
from routes.profile.view import view_bp
from routes.profile.update import update_bp
from routes.profile.blog import blog_bp

profile_bp = Blueprint('profile', __name__)
profile_bp.register_blueprint(view_bp, url_prefix="/profile")
profile_bp.register_blueprint(update_bp)
profile_bp.register_blueprint(blog_bp)

