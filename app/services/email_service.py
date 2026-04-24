import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from ..config import Config

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = Config.SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

def send_fire_alert(user_email, user_name, predicted_class, recommendation, phone=None, address=None, latitude=None, longitude=None):
    # Email to user
    subject_user = f"🔥 Fire Alert: {predicted_class} Detected!"
    body_user = f"""
    🚨 FIRE ALERT 🚨
    
    Dear {user_name},
    
    Fire Class Detected: {predicted_class}
    Recommendation: {recommendation}
    
    Immediate action required!
    Please use the appropriate fire extinguisher as recommended.
    
    Stay Safe!
    IoT Fire Safety System
    """
    send_email(user_email, subject_user, body_user)

    # Email to emergency responders
    subject_emergency = f"🚨 EMERGENCY: {predicted_class} Fire Detected - User: {user_name}"
    
    location_details = ""
    if latitude and longitude:
        location_details = f"\n    Google Maps: https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
    
    body_emergency = f"""
    🚨 EMERGENCY FIRE ALERT 🚨
    
    Fire Class Detected: {predicted_class}
    
    USER DETAILS:
    Name: {user_name}
    Email: {user_email}
    Phone: {phone if phone else 'N/A'}
    Address: {address if address else 'N/A'}
    {location_details}
    
    Recommendation: {recommendation}
    
    IMMEDIATE RESPONSE REQUIRED!
    
    IoT Fire Safety System
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    send_email(Config.EMERGENCY_EMAIL, subject_emergency, body_emergency)

def send_otp_email(to_email, otp):
    subject = "🔐 Dr. Fire - Password Reset OTP"
    body = f"""
    Password Reset Request
    
    Dear User,
    
    You have requested to reset your password for Dr. Fire application.
    
    Your One-Time Password (OTP) is: {otp}
    
    This OTP is valid for 10 minutes.
    
    If you did not request this password reset, please ignore this email.
    
    Stay Safe!
    Dr. Fire Team
    """
    return send_email(to_email, subject, body)

def send_sos_email(user_email, location):
    subject = "🚨 SOS EMERGENCY ALERT 🚨"
    body = f"SOS Alert received from user: {user_email}\nLocation: {location}\nPlease send help immediately!"
    return send_email(Config.EMERGENCY_EMAIL, subject, body)
