import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", os.getenv("SMTP_EMAIL", "")).strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER).strip() or SMTP_USER


def is_smtp_configured() -> bool:
    """Check if SMTP credentials are provided in .env."""
    return bool(SMTP_USER and SMTP_PASSWORD)


def send_otp_email(to_email: str, otp: str, purpose: str = "Email Verification") -> bool:
    """
    Sends a styled OTP verification email to the user's email address.
    If SMTP credentials are not configured or connection fails, logs fallback OTP to console.
    """
    clean_to = to_email.strip().lower()
    subject = f"ChatGPT Verification Code: {otp}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{subject}</title>
    </head>
    <body style="margin: 0; padding: 24px; background-color: #0d1117; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #e6edf3;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 520px; background-color: #161b22; border-radius: 14px; border: 1px solid #30363d; padding: 32px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <tr>
                <td align="center" style="padding-bottom: 24px;">
                    <div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; border-radius: 50%; background: #ffffff; margin-bottom: 12px;">
                        <svg width="34" height="34" viewBox="0 0 24 24" fill="#10a37f" xmlns="http://www.w3.org/2000/svg">
                            <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1683a.071.071 0 0 1 .038.052v5.5826a4.5045 4.5045 0 0 1-4.4945 4.4947zm-9.66-4.1354a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1401-1.6564zm-1.003-9.5218a4.466 4.466 0 0 1 2.3418-1.9729v.1656l-.0048 5.5163a.776.776 0 0 0 .3927.6766l5.8428 3.3732-2.02 1.1683a.0804.0804 0 0 1-.071 0l-4.8303-2.7913a4.4944 4.4944 0 0 1-1.6512-6.1358zm16.597 3.8558-5.8428-3.3732 2.02-1.1683a.0804.0804 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6773a.79.79 0 0 0-.402-.6767zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.776.776 0 0 0-.7854 0L9.409 10.1297V7.7973a.0804.0804 0 0 1 .0332-.0615l4.8303-2.7914a4.4992 4.4992 0 0 1 6.6802 4.6545v.0001zm-12.641 4.1353-2.02-1.1635a.0804.0804 0 0 1-.038-.052v-5.5826a4.4992 4.4992 0 0 1 7.3709-3.4539l-.142.0805-4.7783 2.7582a.7948.7948 0 0 0-.3926.6813v6.732z"/>
                        </svg>
                    </div>
                    <h2 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">ChatGPT Authentication</h2>
                    <p style="margin: 6px 0 0 0; color: #8b949e; font-size: 14px;">{purpose}</p>
                </td>
            </tr>
            <tr>
                <td style="background-color: #0d1117; border-radius: 10px; border: 1px solid #30363d; padding: 24px; text-align: center;">
                    <p style="margin: 0 0 14px 0; color: #c9d1d9; font-size: 14px;">Please use the following verification code to proceed:</p>
                    <div style="display: inline-block; background: rgba(16, 163, 127, 0.15); border: 1.5px solid #10a37f; border-radius: 8px; padding: 12px 28px; font-size: 32px; font-weight: 800; color: #10a37f; letter-spacing: 6px;">
                        {otp}
                    </div>
                    <p style="margin: 16px 0 0 0; color: #8b949e; font-size: 12px;">This code will expire in <strong>10 minutes</strong>. Do not share it with anyone.</p>
                </td>
            </tr>
            <tr>
                <td style="padding-top: 24px; text-align: center; color: #6e7681; font-size: 12px;">
                    If you did not request this email, please ignore it or secure your account.
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    # Always log to backend console as well for instant development inspection
    print(f"\n=======================================================")
    print(f"[OTP NOTIFICATION] {purpose} for: {clean_to}")
    print(f"CODE: >> {otp} << (Valid for 10 minutes)")
    print(f"=======================================================\n")

    if not is_smtp_configured():
        print(f"[EMAIL SERVICE NOTICE] SMTP credentials not set in .env. Email dispatch skipped. OTP logged above.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"ChatGPT <{SMTP_FROM_EMAIL}>"
        msg["To"] = clean_to

        text_fallback = f"Your ChatGPT {purpose} code is: {otp}. It is valid for 10 minutes."
        msg.attach(MIMEText(text_fallback, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=12) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM_EMAIL, [clean_to], msg.as_string())

        print(f"[EMAIL SERVICE SUCCESS] Verification OTP sent successfully to {clean_to} via {SMTP_HOST}!")
        return True
    except Exception as e:
        print(f"[EMAIL SERVICE ERROR] Failed to send email to {clean_to} via SMTP: {e}")
        return False
