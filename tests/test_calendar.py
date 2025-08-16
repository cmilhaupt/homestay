import pytest
from playwright.sync_api import expect, Page
from datetime import datetime, timedelta, UTC
from src.models.booking import Booking
from src.database import db

@pytest.fixture
def clear_bookings(app):
    with app.app_context():
        Booking.query.delete()
        db.session.commit()

def test_calendar_page_loads(page: Page, base_url: str):
    # Login first
    page.goto(f"{base_url}/login")
    page.fill("#access_code", "1234")
    page.click("button[type='submit']")
        
    # Wait for navigation and calendar to load
    page.wait_for_url(f"{base_url}/calendar")
    page.wait_for_selector("#calendar")
    expect(page.locator("#calendar")).to_be_visible()
    expect(page.locator("button:has-text('New Booking')")).to_be_visible()
    expect(page.locator("a:has-text('Logout')")).to_be_visible()

def test_booking_modal_interaction(page: Page, base_url: str):
    # Login and open booking modal
    page.goto(f"{base_url}/login")
    page.fill("#access_code", "1234")
    page.click("button[type='submit']")
    
    # Modal should be hidden initially
    expect(page.locator("#bookingModal")).to_be_hidden()
    
    # Click new booking button and wait for modal
    page.click("button:has-text('New Booking')")
    expect(page.locator("#bookingModal")).to_be_visible()
    
    # Click cancel and wait for modal to hide
    page.click("button:has-text('Cancel')")
    expect(page.locator("#bookingModal")).to_be_hidden()

def test_create_booking_success(page: Page, base_url: str, clear_bookings):
    # Login and open booking modal
    page.goto(f"{base_url}/login")
    page.fill("#access_code", "1234")
    page.click("button[type='submit']")
    page.click("button:has-text('New Booking')")
    
    # Fill booking form
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    day_after = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    
    page.fill("#guestName", "Test Guest")
    page.fill("#guestEmail", "test@example.com")
    page.fill("#startDate", tomorrow)  # Arrival Date
    # Wait for calendar sync
    page.wait_for_timeout(100)
    page.fill("#endDate", day_after)   # Departure Date
    
    # Submit form and wait for response
    page.click("button[type='submit']")
    
    # Wait for calendar to update
    expect(page.locator(".fc-event")).to_be_visible()
    
    # Verify the event spans both arrival and departure dates
    event = page.locator(".fc-event")
    expect(event).to_be_visible()
    # Verify event exists on the correct dates by checking the calendar cell
    tomorrow_cell = page.locator(f"td[data-date='{tomorrow}']")
    day_after_cell = page.locator(f"td[data-date='{day_after}']")
    expect(tomorrow_cell.locator(".fc-event")).to_be_visible()
    expect(day_after_cell.locator(".fc-event")).to_be_visible()

def test_create_booking_validation(page: Page, base_url: str, clear_bookings):
    # Login and open booking modal
    page.goto(f"{base_url}/login")
    page.fill("#access_code", "1234")
    page.click("button[type='submit']")
    page.click("button:has-text('New Booking')")
    
    # Try to submit without required fields and wait
    page.click("button[type='submit']")
    page.wait_for_timeout(500)  # Wait for form validation
    
    # Form shouldn't submit (modal stays open)
    expect(page.locator("#bookingModal")).to_be_visible()
    
    # Fill invalid dates (departure before arrival)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    page.fill("#guestName", "Test Guest")
    page.fill("#guestEmail", "test@example.com")
    page.fill("#startDate", tomorrow)  # Arrival Date
    # Wait for calendar sync
    page.wait_for_timeout(100)
    page.fill("#endDate", yesterday)   # Departure Date
    
    page.click("button[type='submit']")
    
    # Should show error message
    page.wait_for_timeout(500)  # Wait for API response
    expect(page.locator("text=Departure date must be after arrival date")).to_be_visible()

def test_overlapping_booking_prevention(page: Page, base_url: str, clear_bookings, app):
    # Create initial booking
    with app.app_context():
        start_date = datetime.now(UTC) + timedelta(days=1)
        end_date = start_date + timedelta(days=2)
        booking = Booking(
            guest_name="First Guest",
            guest_email="first@example.com",
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(booking)
        db.session.commit()
    
    # Try to create overlapping booking
    page.goto(f"{base_url}/login")
    page.fill("#access_code", "1234")
    page.click("button[type='submit']")
    page.click("button:has-text('New Booking')")
    
    overlap_start = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    overlap_end = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    
    page.fill("#guestName", "Second Guest")
    page.fill("#guestEmail", "second@example.com")
    page.fill("#startDate", overlap_start)
    page.fill("#endDate", overlap_end)
    
    page.click("button[type='submit']")
    
    # Wait for and verify error message
    expect(page.locator("text=Selected dates overlap with existing booking")).to_be_visible()

def test_calendar_displays_existing_bookings(page: Page, base_url: str, clear_bookings, app):
    # Create some bookings
    with app.app_context():
        Booking.query.delete()
        db.session.commit()
        start_date = datetime.now(UTC) + timedelta(days=1)
        end_date = start_date + timedelta(days=2)
        booking1 = Booking(
            guest_name="Test Guest 1",
            guest_email="test1@example.com",
            start_date=start_date,
            end_date=end_date
        )
        booking2 = Booking(
            guest_name="Test Guest 2",
            guest_email="test2@example.com",
            start_date=end_date,
            end_date=end_date + timedelta(days=2)
        )
        db.session.add(booking1)
        db.session.add(booking2)
        db.session.commit()
    
    # View calendar
    page.goto(f"{base_url}/login")
    page.fill("#access_code", "1234")
    page.click("button[type='submit']")
    
    # Should see both bookings
    page.wait_for_timeout(1000)  # Wait longer for calendar to fully load
    events = page.locator('.fc-event')
    expect(events).to_have_count(2)

def test_calendar_navigation(page: Page, base_url: str):
    # Login first
    page.goto(f"{base_url}/login")
    page.fill("#access_code", "1234")
    page.click("button[type='submit']")
    
    # Get initial month/year
    initial_title = page.locator("#calendarTitle").inner_text()
    
    # Click next month button
    page.click("button[aria-label='Next month']")
    page.wait_for_timeout(200)  # Wait for calendar to update
    next_month_title = page.locator("#calendarTitle").inner_text()
    assert next_month_title != initial_title, "Calendar title should change when clicking next"
    
    # Click previous month button twice to go back one month from initial
    page.click("button[aria-label='Previous month']")
    page.click("button[aria-label='Previous month']")
    page.wait_for_timeout(200)  # Wait for calendar to update
    prev_month_title = page.locator("#calendarTitle").inner_text()
    assert prev_month_title != initial_title, "Calendar title should change when clicking previous"
    assert prev_month_title != next_month_title, "Previous and next month titles should be different"
