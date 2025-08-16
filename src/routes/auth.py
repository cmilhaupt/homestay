from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from src.models import User
from src.database import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        access_code = request.form.get('access_code')
        if access_code == current_app.config['DEFAULT_ACCESS_CODE']:
            # Create or get a non-admin user
            user = User.query.filter_by(username='user').first()
            if not user:
                user = User(username='user', password_hash='', is_admin=False)
                db.session.add(user)
                db.session.commit()
            login_user(user)
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('user.calendar'))
        flash('Invalid access code', 'error')
    return render_template('user/login.html')

@bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        access_code = request.form.get('access_code')
        if access_code == current_app.config['ADMIN_ACCESS_CODE']:
            # Create or get admin user
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                default_template = current_app.config['WELCOME_EMAIL_TEMPLATE']
                admin = User(username='admin', password_hash='', is_admin=True, welcome_template=default_template)
                db.session.add(admin)
                db.session.commit()
            login_user(admin)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid access code')
    return render_template('admin/login.html')

@bp.route('/logout')
@login_required
def logout():
    is_admin = current_user.is_admin
    logout_user()
    if is_admin:
        return redirect(url_for('auth.admin_login'))
    return redirect(url_for('auth.login'))
