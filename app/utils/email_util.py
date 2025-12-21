import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

class EmailService:

    @staticmethod
    # Updated HTML Body for the email
    def generate_confirmation_html(client_name, service_name, stylist_name, appointment_date, manage_link):
        
        # colors here for easy reference
        COLOR_MAROON = "#5D0E1F"
        COLOR_GOLD = "#FBBF24"
        COLOR_DARK = "#1c1917"
        COLOR_LIGHT = "#f5f5f4"

        FONT_STACK = "Arial, sans-serif"

        html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Appointment Confirmation</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: {COLOR_LIGHT}; font-family: {FONT_STACK};">

        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed; background-color: {COLOR_LIGHT};">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                        
                        <tr>
                            <td align="center" style="padding: 20px 0 10px 0;">
                                <h1 style="color: {COLOR_MAROON}; font-size: 28px; margin: 0; border-bottom: 3px solid {COLOR_GOLD}; padding-bottom: 10px; width: 80%;">
                                    KC-Afrobraids
                                </h1>
                            </td>
                        </tr>

                        <tr>
                            <td style="padding: 20px 30px 40px 30px;">
                                <h2 style="color: {COLOR_DARK}; font-size: 22px; margin: 0 0 15px 0;">
                                    Hello {client_name},
                                </h2>

                                <p style="color: {COLOR_DARK}; font-size: 16px; line-height: 24px; margin: 0 0 20px 0;">
                                    Thank you for choosing us! Your appointment details are confirmed below.
                                </p>
                                
                                <table border="0" cellpadding="10" cellspacing="0" width="100%" style="border: 1px solid #e0e0e0; border-radius: 4px; margin-bottom: 25px;">
                                    <tr style="background-color: {COLOR_LIGHT};">
                                        <td style="color: {COLOR_DARK}; font-weight: bold; width: 40%;">Service:</td>
                                        <td style="color: {COLOR_DARK};">{service_name}</td>
                                    </tr>
                                    <tr>
                                        <td style="color: {COLOR_DARK}; font-weight: bold;">Stylist:</td>
                                        <td style="color: {COLOR_DARK};">{stylist_name}</td>
                                    </tr>
                                    <tr style="background-color: {COLOR_LIGHT};">
                                        <td style="color: {COLOR_DARK}; font-weight: bold;">Date & Time:</td>
                                        <td style="color: {COLOR_DARK};">{appointment_date}</td>
                                    </tr>
                                </table>


                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td align="center" style="padding: 10px 0;">
                                            <table border="0" cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td align="center" style="border-radius: 25px; background-color: {COLOR_MAROON}; padding: 12px 25px;">
                                                        <a href="{manage_link}" target="_blank" style="color: #ffffff; text-decoration: none; font-weight: bold; font-size: 16px; display: block;">
                                                            Manage Appointment
                                                        </a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                <p style="text-align: center; color: #777; font-size: 14px; margin-top: 30px;">
                                    You can view, reschedule, or cancel your appointment using the link above.
                                </p>
                            </td>
                        </tr>
                        
                        <tr>
                            <td align="center" style="padding: 15px 30px; background-color: {COLOR_MAROON}; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;">
                                <p style="color: #ffffff; font-size: 12px; margin: 0;">
                                    &copy; {2025} The Salon Team. All rights reserved.
                                </p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
        """
        return html_body

    @staticmethod
    def send_appointment_confirmation(client_email, client_name, service_name, stylist_name, appointment_date, manage_link):
        
        # setup the sender emails
        sender_email = os.getenv('sender_email')
        sender_password = os.getenv('app_password')  # use Gmail App Passwords

        subject = "Your Hair Appointment Confirmation"
        # Introducing the edit we made above 
        # Calling the function using the class name
        html_body = EmailService.generate_confirmation_html(
            client_name,
            service_name,
            stylist_name,
            appointment_date,
            manage_link
        )

        # Generate a plain text for fallback purposes
        plain_body = f"""
        Hi {client_name},

        Your appointment for {service_name} with {stylist_name} has been successfully booked for {appointment_date}.

        You can view, reschedule, or cancel your appointment anytime using this secure link:
        {manage_link}

        Best regards,
        The Salon Team
        """

        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = client_email
        msg["Subject"] = subject
        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

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
