
from flask import Blueprint
from routes.profile.blog.api import blog_api_bp
from routes.profile.blog.posts import posts_bp
from routes.profile.blog.new_post import new_post_bp
from routes.profile.blog.delete_post import delete_post_bp
from routes.profile.blog.edit_post import edit_post_bp

blog_bp = Blueprint('blog', __name__)
blog_bp.register_blueprint(blog_api_bp)
blog_bp.register_blueprint(posts_bp)
blog_bp.register_blueprint(new_post_bp)
blog_bp.register_blueprint(delete_post_bp)
blog_bp.register_blueprint(edit_post_bp)
