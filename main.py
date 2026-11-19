@main.route('/make-admin')
@login_required
def make_admin():
    if current_user.username == 'Ki56willy72':   # change to your exact username if different
        current_user.is_admin = True
        db.session.commit()
        flash('You are now an admin.', 'success')
    else:
        flash('Not allowed.', 'danger')
    return redirect(url_for('main.dashboard'))
