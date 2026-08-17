#!/usr/bin/env python3
"""
Simple Email Sender Web App
Frontend form + Flask backend that sends emails via SMTP.
Configure SMTP credentials via environment variables.
"""

import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

# SMTP configuration from environment (required for real sending)
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.mx.cloudflare.net")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "api_token")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "cfut_PJCVt8TjEsw4vxHkqGfubzZvJ6>
FROM_EMAIL = os.environ.get("FROM_EMAIL", "info@registermysite.com")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send_email():
    try:
        to_addr = request.form.get("to", "").strip()
        cc_addr = request.form.get("cc", "").strip()
        bcc_addr = request.form.get("bcc", "").strip()
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()
        is_html = request.form.get("is_html", "false") == "true"

        if not to_addr:
            return jsonify({"success": False, "error": "To address is required"}>
        if not subject:
            return jsonify({"success": False, "error": "Subject is required"}), >
        if not body:
            return jsonify({"success": False, "error": "Body is required"}), 400

        if not SMTP_USER or not SMTP_PASSWORD:
            # Demo mode: just log the email instead of sending
            print("=== DEMO MODE (no SMTP credentials set) ===")
            print(f"To: {to_addr}")
            print(f"CC: {cc_addr}")
            print(f"BCC: {bcc_addr}")
            print(f"Subject: {subject}")
            print(f"HTML: {is_html}")
            print(f"Body:\n{body[:500]}...")
            files = request.files.getlist("attachments")
            for f in files:
                if f and f.filename:
                    print(f"Attachment: {f.filename} ({len(f.read())} bytes)")
                    f.seek(0)
            return jsonify({
                "success": True,
                "message": "Demo mode: email logged to server console (set SMTP_>
            })

        # Build the message
        msg = MIMEMultipart()
        msg["From"] = FROM_EMAIL
        msg["To"] = to_addr
        if cc_addr:
            msg["Cc"] = cc_addr
        msg["Subject"] = subject

        # Recipients list for sendmail
        recipients = [a.strip() for a in to_addr.split(",") if a.strip()]
        if cc_addr:
            recipients += [a.strip() for a in cc_addr.split(",") if a.strip()]
        if bcc_addr:
            recipients += [a.strip() for a in bcc_addr.split(",") if a.strip()]

        # Body
        subtype = "html" if is_html else "plain"
        msg.attach(MIMEText(body, subtype, "utf-8"))

# Attachments
        files = request.files.getlist("attachments")
        for f in files:
            if f and f.filename:
                filename = secure_filename(f.filename)
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={filename}",
                )
                msg.attach(part)


        # Send
        if SMTP_PORT == 465:
            # Implicit SSL (Cloudflare, some other providers)
            context = smtplib.ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as se>
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(FROM_EMAIL, recipients, msg.as_string())
        else:
            # STARTTLS (Gmail, most providers on port 587)
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(FROM_EMAIL, recipients, msg.as_string())

        return jsonify({"success": True, "message": "Email sent successfully!"})

    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Email Sender on http://0.0.0.0:{port}")
    print("Set SMTP_USER, SMTP_PASSWORD (and optionally SMTP_SERVER, SMTP_PORT, >
    app.run(host="0.0.0.0", port=port, debug=True)

