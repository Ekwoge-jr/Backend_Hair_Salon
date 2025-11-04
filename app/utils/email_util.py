import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

class EmailService:

    @staticmethod
    def send_appointment_confirmation(client_email, client_name, service_name, stylist_name, appointment_date, manage_link):
        
        # setup the sender emails
        sender_email = os.getenv('sender_email')
        sender_password = os.getenv('app_password')  # use Gmail App Passwords

        subject = "Your Hair Appointment Confirmation"
        body = f"""
        Hi {client_name},

        Your appointment for **{service_name}** with {stylist_name} has been successfully booked for {appointment_date}.

        You can view, reschedule, or cancel your appointment anytime using this secure link:
        {manage_link}

        Best regards,
        The Salon Team
        """

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = client_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print("✅ Confirmation email sent successfully")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")




"""
# pip install sendgrid
    import os
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    def send_email(to_email, subject, html_content):
        message = Mail(
            from_email = 'no-reply@yourdomain.com',
            to_emails = to_email,
            subject = subject,
            html_content = html_content
        )
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        return response.status_code
"""
