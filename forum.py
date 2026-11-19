import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Post, Reply, Notification
from models import db

forum = Blueprint('forum', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@forum.route('/forum')
def forum_home():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    
    posts_query = Post.query
    if query:
        posts_query = posts_query.filter(
            (Post.title.ilike(f'%{query}%')) | (Post.content.ilike(f'%{query}%'))
        )
    if category:
        posts_query = posts_query.filter_by(category=category)
    
    posts = posts_query.order_by(Post.created_at.desc()).all()
    return render_template('forum.html', posts=posts, query=query, category=category)

@forum.route('/forum/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category', 'General')
        
        attachment_filename = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Prefix with timestamp to avoid collisions
                import time
                filename = f"{int(time.time())}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                attachment_filename = filename

        post = Post(title=title, content=content, category=category, 
                    user_id=current_user.id, attachment=attachment_filename)
        db.session.add(post)
        db.session.commit()
        flash('Transmission uploaded to the grid.', 'success')
        return redirect(url_for('forum.forum_home'))
    return render_template('new_post.html')

@forum.route('/forum/post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST' and current_user.is_authenticated:
        content = request.form.get('content')
        if content:
            reply = Reply(content=content, user_id=current_user.id, post_id=post.id)
            db.session.add(reply)
            # Notify the post author if it's not themselves
            if post.user_id != current_user.id:
                notif = Notification(
                    message=f'{current_user.username} replied to your post: {post.title[:50]}',
                    link=url_for('forum.view_post', post_id=post.id),
                    user_id=post.user_id
                )
                db.session.add(notif)
            db.session.commit()
            flash('Reply transmitted.', 'success')
            return redirect(url_for('forum.view_post', post_id=post.id))
    return render_template('view_post.html', post=post)
