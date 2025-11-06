
from routes.home_page import home_bp
from routes.help import help_bp
from routes.admin import admin_bp
from routes.profile import profile_bp
from routes.view_models import view_models_bp
from routes.chat import chat_bp
from routes.auth import auth_bp, reset_password_bp
from routes.auth.google_auth import google_auth_bp, init_google_oauth
from routes.partners import view_partners_bp

def register_bp(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(profile_bp)
    app.register_blueprint(view_models_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(reset_password_bp)
    app.register_blueprint(view_partners_bp)
    app.register_blueprint(google_auth_bp)
    init_google_oauth(app)
