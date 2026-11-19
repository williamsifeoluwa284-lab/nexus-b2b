from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Message, User, Notification
from app import db

messaging = Blueprint('messaging', __name__)

@messaging.route('/messages')
@login_required
def inbox():
    messages = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.created_at.desc()).all()
    for m in messages:
        if not m.is_read:
            m.is_read = True
    db.session.commit()
    return render_template('inbox.html', messages=messages)

@messaging.route('/messages/new', methods=['GET', 'POST'])
@login_required
def new_message():
    users = User.query.filter(User.id != current_user.id).all()
    preselect = request.args.get('to')
    if request.method == 'POST':
        receiver_id = request.form.get('receiver_id')
        content = request.form.get('content')
        if receiver_id and content:
            msg = Message(content=content, sender_id=current_user.id, receiver_id=int(receiver_id))
            db.session.add(msg)
            # Notify receiver
            notif = Notification(
                message=f'New message from {current_user.username}',
                link=url_for('messaging.inbox'),
                user_id=int(receiver_id)
            )
            db.session.add(notif)
            db.session.commit()
            flash('Message encrypted and delivered.', 'success')
            return redirect(url_for('messaging.inbox'))
    return render_template('new_message.html', users=users, preselect=preselect)