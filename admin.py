from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import User, Post, Notification
from app import db

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('ACCESS DENIED — Admin clearance required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/admin')
@login_required
@admin_required
def dashboard():
    user_count = User.query.count()
    post_count = Post.query.count()
    premium_count = User.query.filter_by(is_premium=True).count()
    return render_template('admin/dashboard.html', 
                           user_count=user_count, 
                           post_count=post_count, 
                           premium_count=premium_count)

@admin.route('/admin/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin.route('/admin/user/<int:user_id>/toggle-premium', methods=['POST'])
@login_required
@admin_required
def toggle_premium(user_id):
    user = User.query.get_or_404(user_id)
    user.is_premium = not user.is_premium
    db.session.commit()
    flash(f'Premium status for {user.username} updated.', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/admin/user/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot remove your own admin status.', 'danger')
        return redirect(url_for('admin.users'))
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f'Admin status for {user.username} updated.', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/admin/posts')
@login_required
@admin_required
def posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/posts.html', posts=posts)

@admin.route('/admin/post/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect(url_for('admin.posts'))
