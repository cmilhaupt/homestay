import pytest
import threading
from playwright.sync_api import Page, expect
from src.app import create_app
from src.database import db

@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'DEFAULT_ACCESS_CODE': '1234',
        'ADMIN_ACCESS_CODE': 'admin1234',
        'SEND_EMAILS': False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope="session")
def test_client(app):
    return app.test_client()

@pytest.fixture(scope="session")
def base_url(app):
    # Start Flask server in a separate thread
    server = threading.Thread(target=lambda: app.run(port=5000))
    server.daemon = True
    server.start()
    
    # Wait for server to start
    import time
    import requests
    from requests.exceptions import ConnectionError
    
    # Try to connect to the server for up to 5 seconds
    start_time = time.time()
    while time.time() - start_time < 5:
        try:
            requests.get('http://localhost:5000')
            break
        except ConnectionError:
            time.sleep(0.1)
    
    return 'http://localhost:5000'
