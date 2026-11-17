from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin_bp.login'

    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.pos import pos_bp
    from app.routes.hotel import hotel_bp
    from app.routes.khata import khata_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(pos_bp, url_prefix='/pos')
    app.register_blueprint(hotel_bp, url_prefix='/hotel-desk')
    app.register_blueprint(khata_bp, url_prefix='/khata')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Automatic self-initialization on startup (ideal for Render & production)
    with app.app_context():
        db.create_all()
        try:
            from app.models import Category
            if not Category.query.first():
                from seed_data import seed_database
                seed_database(app)
        except Exception as e:
            app.logger.warning(f"Auto-seed check: {e}")

    return app
