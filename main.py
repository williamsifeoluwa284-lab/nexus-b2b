import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Post, User
from models import db

main = Blueprint('main', __name__)

ALLOWED_AVATAR = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_avatar(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AVATAR

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', recent_posts=recent_posts)

@main.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)

@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.company = request.form.get('company', '')
        current_user.bio = request.form.get('bio', '')

        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_avatar(file.filename):
                filename = secure_filename(file.filename)
                import time
                filename = f"avatar_{current_user.id}_{int(time.time())}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                current_user.avatar = filename

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('main.profile', username=current_user.username))
    return render_template('edit_profile.html')

@main.route('/users')
def user_directory():
    users = User.query.order_by(User.username).all()
    return render_template('users.html', users=users)
