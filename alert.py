import os
import hashlib
import smtlib
from email.mime.text import MIMETEXT

# EMAIL Configuration

Alert_Server = "smtp.gmail.com
Alert_Port = 587
User_Email = "defaultuser@gmail.com"
User_Password = "!2025IrieBl@ze"
Admin_Email= "admin@safebank.com"

def send_alert(subject,message):
    msg = MIMETEXT(message)
    msg['Subject'] = subject
    msg['From'] = User_Email
    msg['To'] = Admin_Email

    try:
        with smtplib.SMTP(Alert_Server, Alert_Port) as 
            SERVER_SFB: 
           SERVER_SFB.starttls()
              SERVER_SFB.login(User_Email, User_Password)
            SERVER_SFB.sendmail(User_Email, Admin_Email, msg.as_String())
    except Exception as E:
        print(f"Alert Failure")

def Alert():
  subject = "Detected Changes"
  message = "There has beeen detected changes to the FIM System. Review changes and take appropriate action to ensure everything is functioning as expected."
  send_alert(subject,message)

