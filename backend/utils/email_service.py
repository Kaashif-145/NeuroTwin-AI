import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_otp_email(target_email, otp_code):
    """
    Sends a 6-digit OTP code to the specified email address using SMTP.
    """
    load_dotenv(override=True)
    
    server_name = os.getenv("SMTP_SERVER", "smtp.gmail.com").strip()
    port = int(os.getenv("SMTP_PORT", "587")) 
    user = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASS", "").strip()

    if not user or not password:
        print(f"⚠️ [EMAIL SERVICE] SMTP Credentials missing in .env")
        return False, "SMTP credentials missing in .env"

    try:
        msg = MIMEMultipart()
        msg['From'] = f"NeuroTwin AI <{user}>"
        msg['To'] = target_email
        msg['Subject'] = f"{otp_code} is your NeuroTwin Verification Code"
        
        body = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #7928CA; margin: 0;">NeuroTwin AI</h1>
                    <p style="color: #666;">Secure Access Portal</p>
                </div>
                <div style="text-align: center; padding: 20px; border: 1px dashed #7928CA; border-radius: 8px; background: #fafafa;">
                    <p style="font-size: 1.1rem; color: #333;">Your verification code is:</p>
                    <h2 style="font-size: 3rem; color: #FF0080; letter-spacing: 5px; margin: 10px 0;">{otp_code}</h2>
                    <p style="color: #888; font-size: 0.9rem;">This code will expire in 10 minutes.</p>
                </div>
                <p style="color: #555; font-size: 0.9rem; margin-top: 30px; text-align: center;">
                    If you did not request this code, please ignore this email or contact support.
                </p>
                <div style="text-align: center; margin-top: 40px; font-size: 0.8rem; color: #aaa;">
                    © 2026 NeuroTwin AI | Secure Academic Intelligence
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        # Smart Connection Logic
        if port == 465:
            server = smtplib.SMTP_SSL(server_name, port)
        else:
            server = smtplib.SMTP(server_name, port)
            server.set_debuglevel(1) # Enable detailed logs in terminal
            server.starttls()
            
        print(f"🔑 [EMAIL SERVICE] Authenticating {user} on port {port}...")
        server.login(user, password)
        server.send_message(msg)
        server.quit()
        
        return True, "Success"
    except Exception as e:
        print(f"❌ [EMAIL SERVICE] Error: {str(e)}")
        return False, str(e)
