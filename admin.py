from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import User, Post, db

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

@admin.route('/admin/user/<int:user_id
