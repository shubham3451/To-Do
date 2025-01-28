import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from itsdangerous import URLSafeTimedSerializer, BadSignature
from fastapi import HTTPException
from datetime import timedelta

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")

SECRET_KEY = os.getenv("SECRET_KEY")
serializer = URLSafeTimedSerializer(SECRET_KEY)

def send_email(receiver_email: str, subject: str, body: str):
    """Send an email using Gmail SMTP"""
    message = MIMEMultipart()
    message["From"] = EMAIL_SENDER
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        text = message.as_string()
        server.sendmail(EMAIL_SENDER, receiver_email, text)
        server.quit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")

def generate_reset_token(email: str) -> str:
    """Generate a password reset token"""
    return serializer.dumps(email, salt="reset-password-salt")

def verify_reset_token(token: str, expiration_time: timedelta = timedelta(hours=1)) -> str:
    """Verify the password reset token"""
    try:
        email = serializer.loads(token, max_age=expiration_time.total_seconds(), salt="reset-password-salt")
        return email
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
