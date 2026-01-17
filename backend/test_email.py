from dotenv import load_dotenv
load_dotenv()

from app.services.notify_email import send_email

send_email(
    subject="[DailyOps] Email test",
    body="✅ If you got this email, SMTP notifications are working!"
)
print("Sent.")
