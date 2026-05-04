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

    @app.route('/<path:path>')
    def static_proxy(path):
        return send_from_directory('sky', path)

    return app
