from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Notification
from app import db

notifications = Blueprint('notifications', __name__)

@notifications.route('/notifications')
@login_required
def list_notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    # Mark all as read
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('notifications.html', notifications=notifs)

@notifications.route('/notifications/clear', methods=['POST'])
@login_required
def clear_notifications():
    Notification.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('All notifications cleared.', 'success')
    return redirect(url_for('notifications.list_notifications'))
