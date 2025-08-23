import pytest
import threading
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, expect
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

@pytest.fixture(scope="function")
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

@pytest.fixture(scope="function")
def browser():
    """Session-scoped browser - one browser for entire test session"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # or False for debugging
        yield browser
        browser.close()

@pytest.fixture(scope="function")  # Function scope = new context per test
def context(browser: Browser):
    """Function-scoped context - fresh context for each test"""
    context = browser.new_context(
        # Clear state for each test
        viewport={'width': 1280, 'height': 720},
        ignore_https_errors=True,
        # Add any other default settings
    )
    yield context
    context.close()  # Important: close context after each test

@pytest.fixture(scope="function")
def page(context: BrowserContext):
    """Function-scoped page - fresh page for each test"""
    page = context.new_page()
    yield page
    # Page closes automatically when context closes
