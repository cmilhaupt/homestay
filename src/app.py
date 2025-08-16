import logging
from flask import Flask, request, redirect, url_for
from flask_login import LoginManager
from src.config import Config
from src.database import db
from src.models import User
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure logging
    if not app.debug:
        # Set up file handler
        file_handler = logging.FileHandler('instance/booking_app.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
    
    # Always set the app logger level
    app.logger.setLevel(logging.INFO)
    app.logger.info('Booking application startup')

    db.init_app(app)
    with app.app_context():
        db.create_all()
        
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Load welcome template from database if available
    with app.app_context():
        admin = db.session.query(User).filter_by(username='admin').first()
        if admin and admin.welcome_template:
            app.config['WELCOME_EMAIL_TEMPLATE'] = admin.welcome_template
    
    # Custom unauthorized handler to redirect admin routes to admin login
    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith('/admin'):
            return redirect(url_for('auth.admin_login'))
        return redirect(url_for('auth.login'))

    # Register blueprints
    from src.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    try:
        from src.routes.admin import bp as admin_bp
        app.register_blueprint(admin_bp)
    except ImportError:
        app.logger.warning('Admin blueprint not available')

    try:
        from src.routes.user import bp as user_bp
        app.register_blueprint(user_bp)
    except ImportError:
        app.logger.warning('User blueprint not available')

    try:
        from src.routes.api import bp as api_bp
        app.register_blueprint(api_bp)
    except ImportError:
        app.logger.warning('API blueprint not available')

    return app

if __name__ == '__main__':
    app = create_app()
    # Use port 5000 for local development
    app.run(debug=True, port=5000)
