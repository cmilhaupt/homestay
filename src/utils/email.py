import smtplib
import time
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_email(to_email, subject, body, is_html=False, max_retries=3, retry_delay=2):
    """
    Send an email using the configured SMTP server
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Email body content
        is_html (bool): Whether the body is HTML content
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Delay between retries in seconds
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Skip sending emails in test mode
    if not current_app.config.get('SEND_EMAILS', False):
        current_app.logger.info(f"Email sending disabled - would have sent to {to_email}: {subject}")
        return True

    # Get email configuration from app config
    smtp_server = current_app.config['SMTP_SERVER']
    smtp_port = current_app.config['SMTP_PORT']
    smtp_username = current_app.config['SMTP_USERNAME']
    smtp_password = current_app.config['SMTP_PASSWORD']
    from_email = current_app.config['SMTP_FROM_EMAIL']
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    # Attach body
    content_type = 'html' if is_html else 'plain'
    msg.attach(MIMEText(body, content_type))
    
    current_app.logger.info(f"Attempting to send email to {to_email} via {smtp_server}:{smtp_port}")
    
    # Try sending with retries
    for attempt in range(1, max_retries + 1):
        try:
            current_app.logger.debug(f"Email attempt {attempt}/{max_retries}: Connecting to SMTP server")
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                current_app.logger.debug("Starting TLS connection")
                server.starttls()
                current_app.logger.debug(f"Logging in as {smtp_username}")
                server.login(smtp_username, smtp_password)
                current_app.logger.debug(f"Sending message to {to_email}")
                server.send_message(msg)
                current_app.logger.info(f"Email successfully sent to {to_email}")
                return True
        except socket.timeout as e:
            current_app.logger.warning(f"SMTP timeout on attempt {attempt}/{max_retries}: {str(e)}")
        except smtplib.SMTPServerDisconnected as e:
            current_app.logger.warning(f"SMTP server disconnected on attempt {attempt}/{max_retries}: {str(e)}")
        except smtplib.SMTPException as e:
            current_app.logger.warning(f"SMTP error on attempt {attempt}/{max_retries}: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Unexpected error on attempt {attempt}/{max_retries}: {str(e)}")
        
        # Don't sleep after the last attempt
        if attempt < max_retries:
            current_app.logger.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    current_app.logger.error(f"Failed to send email to {to_email} after {max_retries} attempts")
    return False

def send_booking_notification_to_owner(booking):
    """Send notification email to owner about new booking"""
    owner_email = current_app.config['OWNER_EMAIL']
    subject = f"New Booking: {booking.guest_name}"
    
    body = f"""
    A new booking has been created:
    
    Guest: {booking.guest_name}
    Email: {booking.guest_email}
    Check-in: {booking.start_date.strftime('%Y-%m-%d')}
    Check-out: {booking.end_date.strftime('%Y-%m-%d')}
    Created: {booking.created_at.strftime('%Y-%m-%d %H:%M')}
    """
    
    current_app.logger.info(f"Sending booking notification to owner ({owner_email}) for booking ID: {booking.id}")
    result = send_email(owner_email, subject, body)
    if not result:
        current_app.logger.error(f"Failed to send owner notification for booking ID: {booking.id}")
    return result

def send_welcome_email_to_guest(booking):
    """Send welcome email to guest"""
    subject = "Your Booking Confirmation"
    
    # Get welcome message template from app config
    welcome_template = current_app.config.get('WELCOME_EMAIL_TEMPLATE', 
        "Thank you for your booking. We look forward to your stay!")
    
    # Replace placeholders with actual booking data
    body = welcome_template.replace('{guest_name}', booking.guest_name)
    body = body.replace('{start_date}', booking.start_date.strftime('%Y-%m-%d'))
    body = body.replace('{end_date}', booking.end_date.strftime('%Y-%m-%d'))
    
    current_app.logger.info(f"Sending welcome email to guest ({booking.guest_email}) for booking ID: {booking.id}")
    result = send_email(booking.guest_email, subject, body, is_html=True)
    if not result:
        current_app.logger.error(f"Failed to send welcome email to guest for booking ID: {booking.id}")
    return result
