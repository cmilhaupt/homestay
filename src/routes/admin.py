from flask import Blueprint, render_template, redirect, url_for, current_app, request, jsonify
from flask_login import login_required, current_user
from src.models import Booking, User
from src.database import db
from functools import wraps
from datetime import datetime, UTC

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def index():
    return redirect(url_for('admin.dashboard'))

@bp.route('/welcome-template', methods=['PUT'])
@login_required
@admin_required
def update_welcome_template():
    data = request.get_json()
    
    if 'template' not in data or not data['template']:
        return jsonify({'error': 'Welcome email template is required'}), 400
        
    # Update the welcome email template in the database
    admin = User.query.filter_by(username='admin').first()
    admin.welcome_template = data['template']
    db.session.commit()
    
    # Also update the app config for the current session
    current_app.config['WELCOME_EMAIL_TEMPLATE'] = data['template']
    
    return jsonify({'message': 'Welcome email template updated successfully'}), 200

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    bookings = Booking.query.order_by(Booking.start_date.desc()).all()
    
    # Find the next upcoming booking
    now = datetime.now(UTC)
    next_booking = Booking.query.filter(
        Booking.start_date > now
    ).order_by(Booking.start_date.asc()).first()
    
    # Get total number of bookings
    total_bookings = Booking.query.count()
    
    next_guest_info = None
    if next_booking:
        # Ensure start_date is timezone-aware
        start_date = next_booking.start_date.replace(tzinfo=UTC)
        days_until = (start_date - now).days
        next_guest_info = {
            'name': next_booking.guest_name,
            'days': days_until,
            'total_bookings': total_bookings
        }
    
    # Get current access code
    current_code = current_app.config['DEFAULT_ACCESS_CODE']
    
    # Get welcome email template from database
    admin = User.query.filter_by(username='admin').first()
    welcome_template = admin.welcome_template or current_app.config['WELCOME_EMAIL_TEMPLATE']
    
    return render_template('admin/dashboard.html', 
                         bookings=bookings,
                         next_guest_info=next_guest_info,
                         current_code=current_code,
                         welcome_template=welcome_template)
