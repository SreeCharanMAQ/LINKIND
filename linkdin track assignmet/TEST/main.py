from fastapi import FastAPI
from tasks import send_email

app = FastAPI()

@app.post("/send-mail/")
def trigger_email(to: str):
    subject = "Test Email"
    body = "Yo bhai, this is a background email 📩 from FastAPI + Celery"
    send_email.delay(subject, body, to)  # ✅ All 3 args passed
    return {"message": f"Email sent to {to} (background task)"}
