import os
import csv
from flask import Flask, request, jsonify
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from jinja2 import Template

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")

app = Flask(__name__)

# Load the HTML email template
def load_template():
    try:
        with open("email_template.html", "r", encoding='utf-8') as f:
            return Template(f.read())
    except Exception as e:
        print(f"Error loading template: {e}")
        return Template("<p>Template error</p>")

# Load emails from CSV
def load_emails():
    try:
        with open("emails.csv", newline='') as csvfile:
            return list(csv.DictReader(csvfile))
    except Exception as e:
        print(f"Error reading emails.csv: {e}")
        return []

# Send email using SendGrid
def send_email(to_email, subject, html_content):
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✅ Sent to {to_email}: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sending to {to_email}: {e}")

# Root endpoint
@app.route("/")
def home():
    return "Entugo Mailer is Running"

# Endpoint to trigger bulk email send
@app.route("/send", methods=["POST"])
def trigger_send():
    template = load_template()
    recipients = load_emails()

    print(f"📨 Loaded {len(recipients)} recipients from CSV")

    for user in recipients:
        email = user.get("email")
        if email:
            print(f"📧 Sending to: {email}")
            html = template.render()
            send_email(email, "Entugo Warmup - Email Campaign.", html)
        else:
            print("⚠️ Skipped a row due to missing email field")

    return jsonify({"status": "Emails sent"}), 200

# Run the app (Render binds to 0.0.0.0:10000)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
