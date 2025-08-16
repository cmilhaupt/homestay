import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///bookings.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEFAULT_ACCESS_CODE = os.getenv('DEFAULT_ACCESS_CODE', '1234')
    ADMIN_ACCESS_CODE = os.getenv('ADMIN_ACCESS_CODE', 'admin1234')
    
    # Email configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.example.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', 'bookings@example.com')
    OWNER_EMAIL = os.getenv('OWNER_EMAIL', 'owner@example.com')
    SEND_EMAILS = os.getenv('SEND_EMAILS', 'true').lower() == 'true'
    
    # Default welcome email template with placeholders
    WELCOME_EMAIL_TEMPLATE = os.getenv('WELCOME_EMAIL_TEMPLATE', """
    <h2>Thank you for your booking, {guest_name}!</h2>
    
    <p>We're excited to confirm your stay from <strong>{start_date}</strong> to <strong>{end_date}</strong>.</p>
    
    <p>If you have any questions before your arrival, please don't hesitate to contact us.</p>
    
    <p>We look forward to welcoming you!</p>
    """)
