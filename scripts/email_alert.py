import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
import sys

# Configuration for email
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'sutherlandchevon@gmail.com'
SENDER_PASSWORD = 'gjyy lpnl nfyd yfss' 

def send_email_alert(subject, message, recipient='admin@example.com'):
    """
    Send an email alert using SMTP with improved error handling and logging.
    
    Args:
        subject (str): Email subject line
        message (str): Detailed email body
        recipient (str, optional): Email recipient. Defaults to admin email.
    """
    try:
        # Create the email message
        email_message = MIMEMultipart()
        email_message['From'] = SENDER_EMAIL
        email_message['To'] = recipient
        email_message['Subject'] = subject

        # Attach the message body
        email_message.attach(MIMEText(message, 'plain'))

        # Establish a secure session with Gmail's outgoing SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            # Start TLS for security
            server.starttls()
            
            # Login to the server
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            
            # Send the email
            server.send_message(email_message)

        # Log successful email sending
        logging.info(f"Email alert sent: {subject}")
        print(f"Email alert sent: {subject}")

    except smtplib.SMTPAuthenticationError:
        logging.error("SMTP Authentication Failed. Check email and password.")
        print("SMTP Authentication Failed. Verify your credentials.")
    
    except smtplib.SMTPException as smtp_error:
        logging.error(f"SMTP error occurred: {smtp_error}")
        print(f"SMTP error: {smtp_error}")
    
    except Exception as e:
        logging.error(f"Unexpected error sending email: {e}")
        print(f"Error sending email: {e}")

def log_and_alert(event_type, file_path, additional_info=''):
    """
    Log an event and send an email alert.
    
    Args:
        event_type (str): Type of event (e.g., 'NEW_FILE', 'MODIFIED', 'DELETED')
        file_path (str): Path of the affected file
        additional_info (str, optional): Extra details about the event
    """
    # Construct detailed message
    message = f"""FILE INTEGRITY ALERT

Event Type: {event_type}
File Path: {file_path}
Additional Info: {additional_info}

Please investigate this integrity violation immediately.

Regards,
SafeBank File Integrity Monitoring System
"""

    # Send email alert
    send_email_alert(
        f"FIM Alert: {event_type} - {os.path.basename(file_path)}", 
        message
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='email_alerts.log'
)