import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config

def send_email(event, context):
    """
    Lambda function handler for sending emails.
    Supports two triggers: SIGNUP_WELCOME and BOOKING_CONFIRMATION
    """
    try:
        # Parse the event body
        body = json.loads(event.get('body', '{}'))
        trigger = body.get('trigger')
        email = body.get('email')
        data = body.get('data', {})
        
        if not trigger or not email:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields: trigger and email'})
            }
        
        # Get email configuration
        smtp_server = config('SMTP_SERVER', default='smtp.gmail.com')
        smtp_port = config('SMTP_PORT', default=587)
        smtp_username = config('SMTP_USERNAME', default='')
        smtp_password = config('SMTP_PASSWORD', default='')
        
        # Generate email content based on trigger
        subject, body_text = generate_email_content(trigger, data)
        
        # Fallback to local Demo Mode if SMTP credentials are blank/default placeholders
        if not smtp_username or not smtp_password or smtp_username.startswith('your_'):
            print(f"\n[DEMO EMAIL SERVICE] SMTP credentials not set. Running in Demo Mode.")
            print(f"  Recipient: {email}")
            print(f"  Subject: {subject}")
            print(f"  Message Body:\n{body_text}\n")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Email sent successfully (Demo Mode)'})
            }
        
        # Send email
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_text, 'plain'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Email sent successfully'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def generate_email_content(trigger, data):
    """
    Generate email subject and body based on trigger type.
    """
    if trigger == 'SIGNUP_WELCOME':
        username = data.get('username', 'User')
        role = data.get('role', 'User')
        
        subject = 'Welcome to Hospital Management System'
        body = f"""Dear {username},

Welcome to the Hospital Management System!

Your account has been successfully created as a {role}.

If you have any questions, please contact support.

Best regards,
HMS Team
"""
    elif trigger == 'BOOKING_CONFIRMATION':
        patient_name = data.get('patient_name', 'Patient')
        doctor_name = data.get('doctor_name', 'Doctor')
        date = data.get('date', 'N/A')
        start_time = data.get('start_time', 'N/A')
        end_time = data.get('end_time', 'N/A')
        
        subject = 'Booking Confirmation - Hospital Management System'
        body = f"""Dear {patient_name},

Your appointment has been successfully booked!

Appointment Details:
- Doctor: {doctor_name}
- Date: {date}
- Time: {start_time} - {end_time}

Please arrive 10 minutes before your scheduled time.

Best regards,
HMS Team
"""
    else:
        subject = 'Notification from Hospital Management System'
        body = 'You have a new notification from HMS.'
    
    return subject, body
