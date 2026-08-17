 GNU nano 9.1                        README.md
The error is **not** coming from the `server.py` I provided.

Your file (`/data/data/com.termux/files/home/emails/server.py`) contains `import>

### Fix

1. Delete or overwrite your current `server.py`.
2. Use this complete, working version:

```python
#!/usr/bin/env python3
"""
Simple Email Sender Web App
Frontend form + Flask backend that sends emails via SMTP.
Configure SMTP credentials via environment variables.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

# SMTP configuration from environment (required for real sending)
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", SMTP_USER)


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
```


### On Termux

Make sure Flask is installed:

```bash
pip install flask
```

Also make sure you have the `templates/index.html` file in the same folder struc>

```
emails/
├── server.py
└── templates/
    └── index.html
```

Then run:

```bash
python server.py
```
___________________________________________________________

Here’s exactly where to get `SMTP_USER` and `SMTP_PASSWORD`.

### 1. Gmail (most common)

**SMTP_USER** = your full Gmail address
Example: `yourname@gmail.com`

**SMTP_PASSWORD** = a special **App Password** (not your normal Gmail password)

#### How to create a Gmail App Password:

1. Go to your Google Account:
   [https://myaccount.google.com](https://myaccount.google.com)

2. Click **Security** on the left.

3. Under “How you sign in to Google”, make sure **2-Step Verification** is turne>
   (You must have 2-Step Verification enabled to create App Passwords.)

4. After 2-Step Verification is on, go back to the Security page and click **App>

5. Select:
   - App → **Mail**
   - Device → **Other** (type “Email Composer” or anything)

6. Click **Generate**.

7. Google will show you a **16-character password** that looks like:
   `abcd efgh ijkl mnop`

Copy that password (without spaces is fine) — this is your `SMTP_PASSWORD`.
---

### 2. Set the environment variables

In Termux (or any terminal):

```bash
export SMTP_USER="yourname@gmail.com"
export SMTP_PASSWORD="abcdefghijklmnop"   # the 16-character App Password
export FROM_EMAIL="yourname@gmail.com"    # usually the same
```

Then start the server:

```bash
python server.py
```

---

### Other email providers

| Provider       | SMTP_SERVER              | SMTP_PORT | Notes |
|----------------|--------------------------|-----------|-------|
| Gmail          | `smtp.gmail.com`         | 587       | Use App Password |
| Outlook / Hotmail | `smtp.office365.com`  | 587       | Use normal password or>
| Yahoo          | `smtp.mail.yahoo.com`    | 587       | Need App Password |
| Custom / cPanel| Your host’s SMTP server  | 587 or 465| Ask your hosting provi>

---

### Quick tip

If you just want to test the form without sending real emails, **don’t set** `SM>


________________________________________________________________________________>


To send emails from **`info@registermysite.com`** (instead of a Gmail address), >

1. A service that is allowed to send email **as** your domain
2. Correct DNS records (SPF + DKIM + DMARC) so Gmail/Outlook don’t treat the ema>

Here are the best practical options in 2026, ranked by ease for your current Fla>

### 1. Recommended: Resend (easiest & free to start)

Resend is currently one of the best developer experiences and works perfectly wi>

**Steps:**

1. Go to [https://resend.com](https://resend.com) and create a free account.
2. Add your domain `registermysite.com`.
3. Resend will show you a few DNS records (SPF, DKIM, etc.).
   Add them exactly where you manage DNS for the domain (Cloudflare, Namecheap, >
4. Wait until the domain shows as **Verified** (usually 5–30 minutes).
5. Create an **API Key**.
6. Set these environment variables:

```bash
export SMTP_SERVER="smtp.resend.com"
export SMTP_PORT="587"
export SMTP_USER="resend"
export SMTP_PASSWORD="re_xxxxxxxxxxxxxxxx"   # your Resend API key
export FROM_EMAIL="info@registermysite.com"
```

---

### 3. Other good options

| Service          | Best for                  | Free tier          | SMTP ready>
|------------------|---------------------------|--------------------|----------->
| **Resend**       | Developers, simple setup  | 3,000/month        | Yes       >
| **Postmark**     | Highest deliverability    | 100/month          | Yes       >
| **SendGrid**     | Marketing + transactional | 100/day            | Yes       >
| **Amazon SES**   | Cheapest at high volume   | Very cheap         | Yes       >
| **Brevo**        | Budget all-in-one         | 300/day            | Yes       >
| Google Workspace | Real mailboxes            | Paid (~$6/user)    | Yes       >

---

### Important notes

- You **cannot** just invent `info@registermysite.com` and send it through Gmail>
- Always verify the domain (SPF + DKIM) — every service above walks you through >
- For best deliverability, many people send from a subdomain such as `mail.regis>

---

**Quick recommendation:**
Start with **Resend**. It’s the fastest way to go from “works with Gmail” to “se>

Would you like me to also show you the exact DNS records you’ll need, or help yo>
________________________________________________________________________________>

The error `Connection unexpectedly closed` is almost always caused by using the >

### The problem

Your current code does this:

```python
with smtplib.SMTP(...) as server:
    server.starttls()   # ← This is for port 587
```

Cloudflare Email Sending uses **port 465** which requires **SMTP_SSL** (SSL from the very beginning), not STARTTLS.

---

### Fix

Replace the sending part in `server.py` with this improved version that supports both Gmail (587) and Cloudflare (465):

```python
        # Send
        if SMTP_PORT == 465:
            # Implicit SSL (Cloudflare, some other providers)
            context = smtplib.ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(FROM_EMAIL, recipients, msg.as_string())
        else:
            # STARTTLS (Gmail, most providers on port 587)
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(FROM_EMAIL, recipients, msg.as_string())
```

You also need to import `ssl` at the top:

```python
import ssl
```

---

### Correct environment variables for Cloudflare

```bash
export SMTP_SERVER="smtp.mx.cloudflare.net"
export SMTP_PORT="465"
export SMTP_USER="api_token"
export SMTP_PASSWORD="your-cloudflare-api-token"
export FROM_EMAIL="info@registermysite.com"
```

---

### Full corrected sending section

Here’s the complete block you should have in `server.py` (from the comment `# Send` onwards):

```python
        # Send
        if SMTP_PORT == 465:
            # Port 465 = Implicit SSL (Cloudflare)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(FROM_EMAIL, recipients, msg.as_string())
        else:
            # Port 587 = STARTTLS (Gmail, etc.)
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(FROM_EMAIL, recipients, msg.as_string())

        return jsonify({"success": True, "message": "Email sent successfully!"})
```

Don’t forget to add this near the other imports at the top of the file:

```python
import ssl
```

---

After making the change:

1. Save the file
2. Restart the server (`Ctrl+C` then `python server.py`)
3. Try sending an email!

