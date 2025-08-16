from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

bp = Blueprint('user', __name__)

@bp.route('/')
@login_required
def index():
    return redirect(url_for('user.calendar'))

@bp.route('/calendar')
@login_required
def calendar():
    return render_template('user/calendar.html')
