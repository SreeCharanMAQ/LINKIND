from celery import Celery
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("worker", broker=CELERY_BROKER_URL)
@celery_app.task
def send_email_notification(to_email, subject, content):
    print("Sending email notification...")
    sender = "sreecharan94842@gmail.com"
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    msg = MIMEText(content)
    msg["Subject"] = subject
    msg["From"] = "sreechran94842@gmail.com"
    msg["To"] = to_email
    print("Sending mail to:", to_email)
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            message = f"Subject: {subject}\n\n{content}"
            server.sendmail(msg["To"], to_email, msg.as_string())

        print("✅ Mail sent successfully!")

    except Exception as e:
        print("❌ Error sending mail:", e)
