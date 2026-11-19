import os
from flask import Flask
from flask_login import LoginManager
from models import db, User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cyberpunk-b2b-secret-key-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cyberpunk_b2b.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from auth import auth as auth_blueprint
    from main import main as main_blueprint
    from forum import forum as forum_blueprint
    from messaging import messaging as messaging_blueprint
    from payments import payments as payments_blueprint
    from admin import admin as admin_blueprint
    from notifications import notifications as notifications_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(forum_blueprint)
    app.register_blueprint(messaging_blueprint)
    app.register_blueprint(payments_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(notifications_blueprint)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
