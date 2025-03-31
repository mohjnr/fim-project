import os
import hashlib
import smtplib
from email.mime.text import MIMEText

# EMAIL Configuration
Alert_Server = "smtp.gmail.com"
Alert_Port = 587
User_Email = "defaultuser@gmail.com"
User_Password = "!2025IrieBl@ze"
Admin_Email = "admin@safebank.com"

def send_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = User_Email
    msg['To'] = Admin_Email

    try:
        with smtplib.SMTP(Alert_Server, Alert_Port) as server:
            server.starttls()
            server.login(User_Email, User_Password)
            server.sendmail(User_Email, Admin_Email, msg.as_string())
    except Exception as e:
        print(f"Alert Failure: {e}")

def Alert():
    subject = "Detected Changes"
    message = (
        "There have been detected changes to the FIM System. "
        "Review changes and take appropriate action to ensure everything is functioning as expected."
    )
    send_alert(subject, message)
