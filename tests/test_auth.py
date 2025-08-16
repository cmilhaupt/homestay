import pytest
from playwright.sync_api import expect, Page

def test_user_login_success(page: Page, base_url: str, app):
    # Navigate to login page and verify image
    page.goto(f"{base_url}/login")
    expect(page.locator("img[alt='Valencia City of Arts and Sciences']")).to_be_visible()
    
    # Fill in access code and submit
    with app.app_context():
        access_code = app.config['DEFAULT_ACCESS_CODE']
        page.fill("#access_code", access_code)
    page.click("button[type='submit']")
    
    # Verify redirect to calendar page
    expect(page).to_have_url(f"{base_url}/calendar")
    expect(page.locator("h1")).to_contain_text("Booking Calendar")

def test_user_login_failure(page: Page, base_url: str):
    page.goto(f"{base_url}/login")
    
    # Fill in wrong access code
    page.fill("#access_code", "wrong-code")
    page.click("button[type='submit']")
    
    # Should stay on login page with error message
    expect(page).to_have_url(f"{base_url}/login")
    expect(page.locator("text=Invalid access code")).to_be_visible()

def test_admin_login_success(page: Page, base_url: str):
    page.goto(f"{base_url}/admin/login")
    expect(page.locator("img[alt='Valencia City of Arts and Sciences']")).to_be_visible()
    
    # Fill in admin access code
    page.fill("#access_code", "admin1234")
    page.click("button[type='submit']")
    
    # Verify redirect to admin dashboard
    expect(page).to_have_url(f"{base_url}/admin/dashboard")
    expect(page.locator("h1")).to_contain_text("Admin Dashboard")

def test_admin_login_failure(page: Page, base_url: str):
    page.goto(f"{base_url}/admin/login")
    
    # Fill in wrong access code
    page.fill("#access_code", "wrong-code")
    page.click("button[type='submit']")
    
    # Should stay on admin login page with error message
    expect(page).to_have_url(f"{base_url}/admin/login")
    expect(page.locator("text=Invalid access code")).to_be_visible()

def test_user_logout(page: Page, base_url: str):
    # First login as regular user
    page.goto(f"{base_url}/login")
    page.fill("#access_code", "1234")
    page.click("button[type='submit']")
    
    # Wait for calendar page to load
    page.wait_for_url(f"{base_url}/calendar")
    
    # Then logout and wait for navigation
    page.click("text=Logout")
    page.wait_for_url(f"{base_url}/login")
    
    # Verify we're on login page
    expect(page.locator("h1")).to_contain_text("Guest Portal")

def test_admin_logout(page: Page, base_url: str):
    # First login as admin
    page.goto(f"{base_url}/admin/login")
    page.fill("#access_code", "admin1234")
    page.click("button[type='submit']")
    
    # Then logout
    page.click("text=Logout")
    
    # Verify redirect to admin login page
    expect(page).to_have_url(f"{base_url}/admin/login")
