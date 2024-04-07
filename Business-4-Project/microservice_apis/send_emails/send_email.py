import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.conf import settings


def send_email(to_email, subject, code, username):
    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        from_email = Email("fetherstill123@gmail.com")  # Replace with your email

        # Preparing the HTML content
        html_content = f"""
        <p>Hello,</p>

        <p>You're receiving this email because you requested a password reset for your user account at Fetherstill.</p>

        <p>Please use the following code to reset your password: {code}</p>

        <p>Your username, in case you’ve forgotten: {username}</p>

        <p>Thanks for using our site!</p>

        <p>The Fetherstill team</p>
        """

        to_email = To(to_email)
        content = Content("text/html", html_content)
        mail = Mail(from_email, to_email, subject, content)
        response = sg.client.mail.send.post(request_body=mail.get())

        if response.status_code == 202:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error sending email: {e}")
        return False