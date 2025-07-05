import smtplib
from email.mime.text import MIMEText

sender = "sreecharan94842@gmail.com"
password = "mmxdgsyavuqaabzj"  # App password
receiver = "sreecharan9484@gmail.com"  # Send to yourself

msg = MIMEText("Yo bhai, this is a manual SMTP test 😎")
msg["Subject"] = "SMTP Test"
msg["From"] = sender
msg["To"] = receiver

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error sending email: {e}")
