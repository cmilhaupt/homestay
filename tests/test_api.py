import pytest
import time
from flask.testing import FlaskClient
from flask_login import login_user
from src.models import User
from src.database import db
from src.rate_limiting import limiter

@pytest.fixture
def admin_user(app):
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', password_hash='', is_admin=True)
            db.session.add(admin)
            db.session.commit()
        return admin

@pytest.fixture
def regular_user(app):
    with app.app_context():
        user = User.query.filter_by(username='user').first()
        if not user:
            user = User(username='user', password_hash='', is_admin=False)
            db.session.add(user)
            db.session.commit()
        return user

@pytest.fixture(autouse=True)
def reset_limiter():
    """Reset rate limiter between tests"""
    limiter.violations.clear()
    limiter.ban_until.clear()
    limiter.request_times.clear()

def test_rate_limit_basic(test_client: FlaskClient):
    """Test basic rate limiting (3 requests per second)"""
    # First 3 requests should succeed
    for _ in range(3):
        response = test_client.get('/api/bookings')
        assert response.status_code != 429
    
    # 4th request should be rate limited
    response = test_client.get('/api/bookings')
    assert response.status_code == 429
    assert b"Too many requests" in response.data

def test_rate_limit_ban(test_client: FlaskClient):
    """Test ban after repeated violations"""
    # Trigger rate limit multiple times
    for _ in range(2):
        for _ in range(4):  # Exceed per-second limit
            test_client.get('/api/bookings')
        time.sleep(1.1)  # Wait for first ban to expire
    
    # Should now be banned with longer duration
    response = test_client.get('/api/bookings')
    assert response.status_code == 429
    assert b"Rate limit exceeded" in response.data

def test_update_access_code_success(test_client: FlaskClient, app, admin_user):
    with app.app_context():
        db.session.add(admin_user)
        db.session.refresh(admin_user)
        with app.test_request_context():
            login_user(admin_user)
            response = test_client.put('/api/access-code', json={'code': '5678'})
            assert response.status_code == 200
            assert response.json['message'] == 'Access code updated successfully'
            assert app.config['DEFAULT_ACCESS_CODE'] == '5678'

def test_update_access_code_unauthorized(test_client: FlaskClient, app, regular_user):
    with app.app_context():
        db.session.add(regular_user)
        db.session.refresh(regular_user)
        with app.test_request_context():
            login_user(regular_user)
            response = test_client.put('/api/access-code', json={'code': '5678'})
            assert response.status_code == 403
            assert response.json['error'] == 'Admin access required'

def test_update_access_code_empty(test_client: FlaskClient, app, admin_user):
    with app.test_request_context():
        login_user(admin_user)
        response = test_client.put('/api/access-code', json={'code': ''})
        assert response.status_code == 400
        assert response.json['error'] == 'New access code is required'

def test_update_access_code_missing_code(test_client: FlaskClient, app, admin_user):
    with app.test_request_context():
        login_user(admin_user)
        response = test_client.put('/api/access-code', json={})
        assert response.status_code == 400
        assert response.json['error'] == 'New access code is required'
