import os
import hashlib
import smtplib
from email.mime.text import MIMEText

# EMAIL Configuration
# Credentials for alert notification

Alert_Server = "smtp.gmail.com"
Alert_Port = 587
User_Email = "defaultuser@gmail.com"
User_Password = "!2025IrieBl@ze"
Admin_Email= "admin@safebank.com"

# Function for sending alerts

# Defining alert message information 
def send_alert(subject,message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = User_Email
    msg['To'] = Admin_Email
    
# Sending an email alert using the Simple Mail Transfer Protocol (SMTP)
    try:
        with smtplib.SMTP(Alert_Server, Alert_Port) as SERVER_SFB:
            SERVER_SFB.starttls()
            SERVER_SFB.login(User_Email, User_Password)
            SERVER_SFB.sendmail(User_Email, Admin_Email, msg.as_string())
    except Exception as E:
        print(f"Alert Failure")
        
# Alert function
def Alert():
  subject = "Detected Changes"
  message = "There has beeen detected changes to the FIM System. Review changes and take appropriate action to ensure everything is functioning as expected."
  send_alert(subject,message)

