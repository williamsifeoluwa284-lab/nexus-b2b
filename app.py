import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cyberpunk-b2b-secret-key-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cyberpunk_b2b.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB limit
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'ACCESS DENIED — Authenticate to proceed.'
    login_manager.login_message_category = 'danger'

    from models import User

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

    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        from models import Message, Notification
        unread_messages = 0
        unread_notifs = 0
        if current_user.is_authenticated:
            unread_messages = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
            unread_notifs = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return dict(unread=unread_messages, unread_notifs=unread_notifs)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)