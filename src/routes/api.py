from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime
from src.models import Booking, BlockedDate
from src.database import db
from functools import wraps
from src.rate_limiting import limiter
from src.utils.email import send_booking_notification_to_owner, send_welcome_email_to_guest

bp = Blueprint('api', __name__, url_prefix='/api')

def rate_limit_check():
    """Check rate limits and return appropriate response if limit exceeded"""
    ip = request.remote_addr
    if limiter.is_banned(ip):
        return jsonify({
            'error': 'Rate limit exceeded. Please try again later.'
        }), 429
    if not limiter.check_rate_limit(ip):
        return jsonify({
            'error': 'Too many requests. Please slow down.'
        }), 429
    return None

@bp.before_request
def check_rate_limit():
    """Apply rate limiting to all API routes"""
    if request.endpoint:  # Skip if no endpoint (e.g., OPTIONS requests)
        response = rate_limit_check()
        if response is not None:
            return response

@bp.route('/bookings', methods=['GET'])
@login_required
def get_bookings():
    bookings = Booking.query.all()
    blocked_dates = BlockedDate.query.all()
    
    events = []
    
    # Add regular bookings
    for booking in bookings:
        events.append({
            'id': booking.id,
            'start': booking.start_date.isoformat(),
            'end': booking.end_date.isoformat(),
            'title': 'Booked',
            'type': 'booking',
            'guest_name': booking.guest_name,
            'guest_email': booking.guest_email
        })
    
    # Add blocked dates (appear the same to regular users)
    for blocked in blocked_dates:
        events.append({
            'id': blocked.id,
            'start': blocked.start_date.isoformat(),
            'end': blocked.end_date.isoformat(),
            'title': 'Booked',
            'type': 'blocked',
            'reason': blocked.reason
        })
    
    return jsonify(events)

@bp.route('/bookings/<int:booking_id>', methods=['DELETE'])
@login_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    return jsonify({'message': 'Booking deleted successfully'}), 200

@bp.route('/bookings', methods=['POST'])
@login_required
def create_booking():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['guest_name', 'guest_email', 'start_date', 'end_date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Parse dates
    try:
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date'])
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Check for date validity
    if end_date <= start_date:
        return jsonify({'error': 'Departure date must be after arrival date'}), 400
    
    # Check for overlapping bookings
    overlapping_booking = Booking.query.filter(
        db.or_(
            db.and_(Booking.start_date <= start_date, Booking.end_date >= start_date),
            db.and_(Booking.start_date <= end_date, Booking.end_date >= end_date),
            db.and_(Booking.start_date >= start_date, Booking.end_date <= end_date)
        )
    ).first()
    
    # Check for overlapping blocked dates
    overlapping_blocked = BlockedDate.query.filter(
        db.or_(
            db.and_(BlockedDate.start_date <= start_date, BlockedDate.end_date >= start_date),
            db.and_(BlockedDate.start_date <= end_date, BlockedDate.end_date >= end_date),
            db.and_(BlockedDate.start_date >= start_date, BlockedDate.end_date <= end_date)
        )
    ).first()
    
    if overlapping_booking or overlapping_blocked:
        return jsonify({'error': 'Selected dates overlap with existing booking'}), 400
    
    # Create new booking
    booking = Booking(
        guest_name=data['guest_name'],
        guest_email=data['guest_email'],
        start_date=start_date,
        end_date=end_date
    )
    
    db.session.add(booking)
    db.session.commit()
    
    # Send email notifications
    owner_email_sent = send_booking_notification_to_owner(booking)
    guest_email_sent = send_welcome_email_to_guest(booking)
    
    if not owner_email_sent or not guest_email_sent:
        current_app.logger.warning(
            f"Booking created but email notifications may have failed. "
            f"Owner email: {'sent' if owner_email_sent else 'failed'}, "
            f"Guest email: {'sent' if guest_email_sent else 'failed'}"
        )
    
    return jsonify({'message': 'Booking created successfully'}), 201

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/access-code', methods=['PUT'])
@login_required
@admin_required
def update_access_code():
    data = request.get_json()
    
    if 'code' not in data or not data['code']:
        return jsonify({'error': 'New access code is required'}), 400
        
    # Update the access code in the app config
    current_app.config['DEFAULT_ACCESS_CODE'] = data['code']
    
    return jsonify({'message': 'Access code updated successfully'}), 200

@bp.route('/blocked-dates', methods=['POST'])
@login_required
@admin_required
def create_blocked_date():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['start_date', 'end_date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Parse dates
    try:
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date'])
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Check for date validity
    if end_date <= start_date:
        return jsonify({'error': 'End date must be after start date'}), 400
    
    # Check for overlapping bookings
    overlapping_booking = Booking.query.filter(
        db.or_(
            db.and_(Booking.start_date <= start_date, Booking.end_date >= start_date),
            db.and_(Booking.start_date <= end_date, Booking.end_date >= end_date),
            db.and_(Booking.start_date >= start_date, Booking.end_date <= end_date)
        )
    ).first()
    
    # Check for overlapping blocked dates
    overlapping_blocked = BlockedDate.query.filter(
        db.or_(
            db.and_(BlockedDate.start_date <= start_date, BlockedDate.end_date >= start_date),
            db.and_(BlockedDate.start_date <= end_date, BlockedDate.end_date >= end_date),
            db.and_(BlockedDate.start_date >= start_date, BlockedDate.end_date <= end_date)
        )
    ).first()
    
    if overlapping_booking or overlapping_blocked:
        return jsonify({'error': 'Selected dates overlap with existing booking or blocked period'}), 400
    
    # Create new blocked date
    blocked_date = BlockedDate(
        start_date=start_date,
        end_date=end_date,
        reason=data.get('reason', '')
    )
    
    db.session.add(blocked_date)
    db.session.commit()
    
    return jsonify({'message': 'Blocked date created successfully'}), 201

@bp.route('/blocked-dates/<int:blocked_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_blocked_date(blocked_id):
    blocked_date = BlockedDate.query.get_or_404(blocked_id)
    db.session.delete(blocked_date)
    db.session.commit()
    return jsonify({'message': 'Blocked date deleted successfully'}), 200
