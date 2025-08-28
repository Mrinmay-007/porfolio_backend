


from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
from pydantic import EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Optional


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://portfolio-website-eta-eight-67.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # <-- ensures OPTIONS, POST, GET etc are allowed
    allow_headers=["*"],
)


# origins = [
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
#     "https://portfolio-website-eta-eight-67.vercel.app"
# ]


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],

# )


# ---- Your Email Config ----
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
MY_EMAIL = "projtest2025@gmail.com"
MY_PASSWORD = "qpazhkxtwdykouzq"  # Gmail app password (no spaces)

# ---- Utility ----
def send_to_me(user_name: str, user_email: str, subject: str, message: str, file_content: Optional[bytes] = None, filename: Optional[str] = None):
    """
    Constructs and sends an email with optional attachment.
    """
    msg = MIMEMultipart()
    msg["From"] = user_email
    msg["To"] = MY_EMAIL
    msg["Subject"] = f"[Contact Form] {subject}"

    # Body text
    body = f"""
    You received a new message from {user_name} <{user_email}>:

    {message}
    """
    msg.attach(MIMEText(body, "plain"))

    # If a file was uploaded, attach it
    if file_content and filename:
        part = MIMEApplication(file_content, Name=filename)
        part['Content-Disposition'] = f'attachment; filename="{filename}"'
        msg.attach(part)

    # Send email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(MY_EMAIL, MY_PASSWORD)
            server.sendmail(user_email, MY_EMAIL, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


# ---- Route ----
@app.post("/contact/")
async def contact(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: EmailStr = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """
    Handles the contact form submission.
    Reads an optional uploaded file and schedules an email to be sent in the background.
    """
    file_content = None
    filename = None
    if file:
        file_content = await file.read()
        filename = file.filename

    # Pass raw bytes + filename to background task
    background_tasks.add_task(
        send_to_me, name, email, subject, message, file_content, filename
    )
    return {"message": "✅ Your message has been sent successfully!"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
