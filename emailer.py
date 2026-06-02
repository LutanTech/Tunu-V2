from flask_mail import Mail, Message
from flask import render_template_string

mail = Mail()

# ========================
# HTML TEMPLATES
# ========================
def compose_mail(name, id, password):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #f4f7f6;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            .header {{
                background-color: #8B008B;
                padding: 40px 20px;
                text-align: center;
            }}
            .logo {{
                width: 80px;
                height: auto;
                filter: brightness(0) invert(1);
            }}
            .content {{
                padding: 40px 30px;
                color: #2d3436;
                line-height: 1.6;
            }}
            .welcome-text {{
                font-size: 24px;
                font-weight: 700;
                color: #4B004B;
                margin-bottom: 20px;
            }}
            .credentials-box {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 25px;
                margin: 25px 0;
            }}
            .credential-item {{
                margin-bottom: 10px;
                font-size: 16px;
            }}
            .credential-label {{
                color: #64748b;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 12px;
                display: block;
                margin-bottom: 4px;
            }}
            .credential-value {{
                font-family: 'Courier New', monospace;
                font-size: 18px;
                font-weight: 700;
                color: #1a1a1a;
            }}
            .cta-button {{
                display: inline-block;
                padding: 14px 30px;
                background-color: #FF4500;
                color: #ffffff !important;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 700;
                margin-top: 20px;
            }}
            .footer {{
                padding: 25px;
                text-align: center;
                background-color: #1e1e1e;
                color: #94a3b8;
                font-size: 12px;
            }}
            .warning-text {{
                color: #ef4444;
                font-size: 13px;
                margin-top: 20px;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <img src="https://i.ibb.co/CKRYPD4p/image.png" alt="TUNU Logo" class="logo">
                <div style="color: white; margin-top: 15px; font-weight: 800; letter-spacing: 2px; font-size: 14px;">STAFF ONBOARDING</div>
            </div>
            
            <div class="content">
                <div class="welcome-text">Welcome to the team, {name}! 👋</div>
                <p>Your official staff account at <b>TUNU Publishers</b> has been successfully provisioned. You can now access the executive dashboard using the credentials provided below.</p>
                
                <div class="credentials-box">
                    <div class="credential-item">
                        <span class="credential-label">Staff Identification</span>
                        <span class="credential-value">{id}</span>
                    </div>
                    <div class="credential-item">
                        <span class="credential-label">Temporary Password</span>
                        <span class="credential-value">{password}</span>
                    </div>
                </div>

                <center>
                    <a target="_blank" href="https://tunu-publishers.com/staff/login" class="cta-button">Access Dashboard</a>
                </center>

                <p class="warning-text" style="text-align:center">
                    ⚠️ <br>
                    Security Notice <br> You are required to change this temporary password immediately upon your first login for account security.
                </p>
            </div>

            <div class="footer">
                <p>&copy; 2026 TUNU Publishers. All rights reserved.</p>
                <p> Harambee SACCO, Donholm, Nairobi, Kenya</p>
            </div>
        </div>
    </body>
    </html>
    """

REMINDER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { margin: 0; padding: 0; background-color: #f4f7f6; font-family: 'Segoe UI', Arial, sans-serif; }
        .email-container { max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .header { background-color: #1e1e1e; padding: 30px 20px; text-align: center; border-bottom: 4px solid #8B008B; }
        .logo { width: 60px; height: auto; filter: brightness(0) invert(1); }
        .content { padding: 40px 30px; color: #2d3436; line-height: 1.6; }
        .title-text { font-size: 22px; font-weight: 700; color: #1a1a1a; margin-bottom: 15px; }
        .task-list { background-color: #fff5f2; border-left: 4px solid #FF4500; padding: 20px; margin: 25px 0; border-radius: 0 12px 12px 0; }
        .task-item { margin-bottom: 12px; font-size: 15px; color: #4b5563; list-style: none; }
        .cta-button { display: inline-block; padding: 14px 30px; background-color: #8B008B; color: #ffffff !important; text-decoration: none; border-radius: 8px; font-weight: 700; margin-top: 10px; }
        .footer { padding: 20px; text-align: center; background-color: #f8fafc; color: #94a3b8; font-size: 12px; border-top: 1px solid #e2e8f0; }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <img src="https://i.ibb.co/CKRYPD4p/image.png" alt="TUNU Logo" class="logo">
        </div>
        <div class="content">
            <div class="title-text">Daily System Reminder ⏰</div>
            <p>Hello Team, this is a scheduled reminder to ensure all field activities and administrative tasks are up to date for the day.</p>
            <div class="task-list">
                <div class="task-item">🔹 Review your personal dashboard</div>
                <div class="task-item">🔹 Finalize all pending field tasks</div>
                <div class="task-item">🔹 Submit your mandatory daily report</div>
            </div>
            <p>Consistent reporting ensures your field efforts are accurately captured in the executive panel.</p>
            <center>
                <a href="#" class="cta-button">Open Staff Portal</a>
            </center>
        </div>
        <div class="footer">
            <p>Automated System Message • TUNU Publishers</p>
            <p>Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""


WEEKEND_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        .container { max-width: 600px; margin: auto; font-family: 'Segoe UI', Arial; border: 1px solid #eee; border-radius: 15px; overflow: hidden; }
        .banner { background: #8B008B; padding: 30px; text-align: center; }
        .content { padding: 35px; color: #333; line-height: 1.8; text-align: center; }
        .map-section { background: #f8fafc; padding: 20px; border-radius: 12px; margin-top: 25px; border: 1px dashed #cbd5e1; }
        .btn-map { 
            display: inline-block; 
            padding: 12px 25px; 
            background: #FF4500; 
            color: white !important; 
            text-decoration: none; 
            border-radius: 8px; 
            font-weight: bold; 
            margin-top: 15px;
        }
        .footer { background: #f1f5f9; color: #64748b; padding: 20px; text-align: center; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="banner">
            <img src="https://i.ibb.co/CKRYPD4p/image.png" width="60" style="filter: brightness(0) invert(1);">
        </div>
        <div class="content">
            <h2 style="color: #8B008B;">Happy Friday! ✨</h2>
            <p>It was a pleasure connecting with you at <b>{{ location }}</b> this week.</p>
            <p>The team at <b>TUNU Publishers</b> wishes you a restful and wonderful weekend. We look forward to our next meeting!</p>
            
            <div class="map-section">
                <p style="margin:0; font-size: 14px; font-weight: 600;">Find us or track our field progress:</p>
                <a href="https://maps.app.goo.gl/ndW1VRXwcVjcvHC6A" class="btn-map">
                    <i class="fas fa-map-marker-alt"></i> View on Google Maps
                </a>
            </div>
        </div>
        <div class="footer">
            &copy; 2026 TUNU Publishers | Nairobi, Kenya
        </div>
    </div>
</body>
</html>
"""





# ========================
# SEND WELCOME EMAIL
# ========================
def send_welcome_message(staff):
    msg = Message(
        subject="Welcome to Tunu Staff 🎉",
        recipients=[staff.email]
    )

    msg.html = compose_mail(staff.name, staff.id, '#TunuStaff2026')

    mail.send(msg)


# ========================
# SEND REMINDER TO MANY
# ========================
def send_reminder(emails: list):
    if not emails:
        return False

    msg = Message(
        subject="System Reminder ⏰",
        recipients=[emails[0]], 
        bcc=emails[1:] if len(emails) > 1 else None
    )

    msg.html = REMINDER_HTML

    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send reminder: {e}")
        return False
    

from flask import render_template_string
from flask_mail import Message
MAP_LINK = "https://maps.app.goo.gl/ndW1VRXwcVjcvHC6A"

def send_weekend_wish(contacts: list):
    """
    contacts: A list of tuples/objects containing (email, location_name)
    """
    from app import mail 
    
    success_count = 0
    seen_emails = set()

    for email, location in contacts:
        if not email or "@" not in email:
            continue
            
        clean_email = email.strip().lower()
        if clean_email in seen_emails:
            continue

        msg = Message(
            subject="Wishing you a wonderful weekend! ✨",
            recipients=[clean_email]
        )
        
        msg.html = render_template_string(f"""
        <div style="font-family: Arial; text-align: center; padding: 40px; border: 1px solid #eee; border-radius: 15px;">
            <img src="https://i.ibb.co/CKRYPD4p/image.png" width="60" style="margin-bottom: 20px;">
            <h2 style="color: #8B008B;">Happy Friday! ✨</h2>
            <p>It was a pleasure connecting with you at <b>{{{{ location }}}}</b>.</p>
            <p>The team at <b>TUNU Publishers</b> wishes you a restful weekend.</p>
            <div style="margin: 30px 0;">
                <a href="{MAP_LINK}" style="background: #FF4500; color: white; padding: 12px 25px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    📍 Visit Our Office
                </a>
            </div>
            <p style="font-size: 12px; color: grey;">Nairobi, Kenya</p>
        </div>
        """, location=location)
        
        try:
            mail.send(msg)
            seen_emails.add(clean_email)
            success_count += 1
        except Exception:
            pass

    return success_count