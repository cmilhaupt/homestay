import pytest
from playwright.sync_api import expect, Page
from datetime import datetime, timedelta, UTC
from src.models.booking import Booking
from src.database import db

@pytest.fixture
def sample_booking(app):
    with app.app_context():
        booking = Booking(
            guest_name="Test Guest",
            guest_email="test@example.com",
            start_date=datetime.now(UTC),
            end_date=datetime.now(UTC) + timedelta(days=2)
        )
        db.session.add(booking)
        db.session.commit()
        return booking

def test_admin_dashboard_shows_bookings(page: Page, base_url: str, sample_booking):
    # Login as admin first
    page.goto(f"{base_url}/admin/login")
    page.fill("#access_code", "admin1234")
    page.click("button[type='submit']")
    
    # Verify booking appears in table
    expect(page.locator("#bookingsTable")).to_be_visible()
    expect(page.locator("#bookingsTable td:has-text('Test Guest')")).to_be_visible()
    expect(page.locator("#bookingsTable td:has-text('test@example.com')")).to_be_visible()

def test_admin_dashboard_shows_access_code(page: Page, base_url: str, app):
    # Login as admin
    page.goto(f"{base_url}/admin/login")
    page.fill("#access_code", "admin1234")
    page.click("button[type='submit']")
    
    # Verify access code section exists and shows current code
    expect(page.locator("#currentCode")).to_be_visible()
    expect(page.locator("#currentCode")).to_have_value("1234")
    expect(page.locator("#newCode")).to_be_visible()

def test_update_access_code_success(page: Page, base_url: str, app):
    # Login as admin
    page.goto(f"{base_url}/admin/login")
    page.fill("#access_code", "admin1234")
    page.click("button[type='submit']")
    
    # Update access code
    page.fill("#newCode", "5678")
    page.click("button:text('Update')")
    
    # Wait for page reload and verify new code
    page.wait_for_load_state("networkidle")
    expect(page.locator("#currentCode")).to_have_value("5678")

def test_update_access_code_empty(page: Page, base_url: str, app):
    # Login as admin
    page.goto(f"{base_url}/admin/login")
    page.fill("#access_code", "admin1234")
    page.click("button[type='submit']")
    
    # Try to update with empty code
    page.fill("#newCode", "")
    page.click("button:text('Update')")
    
    # Verify error message
    page.wait_for_timeout(500)  # Wait for alert
    expect(page.locator("text=Please enter a new access code")).to_be_visible()

def test_admin_dashboard_no_bookings(page: Page, base_url: str, app):
    # Clear all bookings
    with app.app_context():
        Booking.query.delete()
        db.session.commit()
    
    # Login as admin
    page.goto(f"{base_url}/admin/login")
    page.fill("#access_code", "admin1234")
    page.click("button[type='submit']")
    
    # Verify "No bookings found" message
    expect(page.locator("text=No bookings found")).to_be_visible()
