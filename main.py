from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import User, Post, db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    recent_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', recent_posts=recent_posts)

@main.route('/directory')
@login_required
def user_directory():
    users = User.query.filter(User.id != current_user.id).order_by(User.username).all()
    return render_template('users.html', users=users)

@main.route('/profile/<int:user_id>')
@login_required
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.company = request.form.get('company')
        current_user.bio = request.form.get('bio')
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('edit_profile.html')

@main.route('/make-admin')
@login_required
def make_admin():
    current_user.is_admin = True
    db.session.commit()
    flash('You are now an admin.', 'success')
    return redirect(url_for('main.dashboard'))
