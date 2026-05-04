from flask import Flask, send_from_directory, Blueprint

from flask_login import LoginManager

from config import Config

from extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Log in to access dashboard.'

    from models import Admin
    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    # Routes
    from routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/')

    from routes.opportunities import bp as opp_bp
    app.register_blueprint(opp_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return send_from_directory('sky', 'admin.html')

    @app.route('/admin.css')
    def admin_css():
        return send_from_directory('sky', 'admin.css')

    @app.route('/admin.js')
    def admin_js():
        return send_from_directory('sky', 'admin.js')

    @app.route('/demo-login')
    def demo_login():
        from flask_login import login_user
        from models import Admin
        admin = Admin.query.filter_by(email='demo@admin.com').first()
        if admin:
            login_user(admin)
            return {'success': True, 'message': 'Demo login - email: demo@admin.com'}
        return {'error': 'Demo user not found'}, 404

    @app.route('/<path:path>')
    def static_proxy(path):
        return send_from_directory('sky', path)

    with app.app_context():
        db.create_all()
        # Create demo user if not exists
        if not Admin.query.filter_by(email='demo@admin.com').first():
            demo = Admin(full_name='Demo Admin', email='demo@admin.com')
            demo.set_password('demopass123')
            db.session.add(demo)
            db.session.commit()

    return app

