@main.route('/make-admin')
@login_required
def make_admin():
    current_user.is_admin = True
    db.session.commit()
    flash('You are now an admin.', 'success')
    return redirect(url_for('main.dashboard'))
