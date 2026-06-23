from app.core.config import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# -------------------------------
# Helper function to send email
# -------------------------------
def send_email(to_email, subject, html_content, from_email="hlearningsarl@gmail.com"):
    """
    Send an email using SendGrid
    """
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"[SENDGRID] Email sent to {to_email} | Status code: {response.status_code}")
        return True
    except Exception as e:
        print(f"[SENDGRID] Error sending email to {to_email}: {e}")
        return False

# -------------------------------
# Email templates (HTML)
# -------------------------------

def welcome_email(name):
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #2B0A5B;">
            <h2>Welcome to H-Learning, {name}!</h2>
            <p>Thank you for signing up. Start exploring our premium courses today!</p>
            <p><a href="https://h-learning.com/login" style="padding: 10px 20px; background-color: #2B0A5B; color: white; text-decoration: none; border-radius: 8px;">Login Now</a></p>
        </body>
    </html>
    """

def login_alert_email(name, ip_address):
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #2B0A5B;">
            <h2>Login Alert</h2>
            <p>Hello {name}, we noticed a login to your account from IP: {ip_address}.</p>
            <p>If this was you, no action is needed. Otherwise, please secure your account immediately.</p>
            <p><a href="https://h-learning.com/security" style="padding: 10px 20px; background-color: #2B0A5B; color: white; text-decoration: none; border-radius: 8px;">Secure Account</a></p>
        </body>
    </html>
    """

def otp_email(otp_code):
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #2B0A5B;">
            <h2>Your H-Learning OTP Code</h2>
            <p>Use the code below to verify your account:</p>
            <h3 style="background-color: #f1f1f1; display: inline-block; padding: 10px 20px; border-radius: 8px;">{otp_code}</h3>
            <p>This code will expire in 5 minutes.</p>
        </body>
    </html>
    """

def subscription_email(course_name):
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #2B0A5B;">
            <h2>Subscription Confirmed!</h2>
            <p>Thank you for subscribing to <strong>{course_name}</strong>.</p>
            <p>Start learning now and unlock your full potential!</p>
            <p><a href="https://h-learning.com/courses/{course_name.replace(' ', '-').lower()}" style="padding: 10px 20px; background-color: #2B0A5B; color: white; text-decoration: none; border-radius: 8px;">Go to Course</a></p>
        </body>
    </html>
    """

def request_response_email(request_title, status):
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #2B0A5B;">
            <h2>Update on Your Request</h2>
            <p>Your request: <strong>{request_title}</strong> has been <strong>{status}</strong>.</p>
            <p>Thank you for using H-Learning!</p>
        </body>
    </html>
    """

# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    send_email("user@example.com", "Welcome to H-Learning!", welcome_email("John"))
    send_email("user@example.com", "Login Alert", login_alert_email("John", "192.168.0.1"))
    send_email("user@example.com", "Your OTP Code", otp_email("123456"))
    send_email("user@example.com", "Subscription Confirmed", subscription_email("English"))
    send_email("user@example.com", "Request Update", request_response_email("Course Access", "Approved"))
