"""
Email service for sending notifications
"""
import os
import logging
from typing import List, Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

logger = logging.getLogger(__name__)

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@example.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() == "true",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() == "true",
    USE_CREDENTIALS=os.getenv("USE_CREDENTIALS", "True").lower() == "true",
    VALIDATE_CERTS=os.getenv("VALIDATE_CERTS", "True").lower() == "true",
)

# Check if email is configured
EMAIL_ENABLED = bool(os.getenv("MAIL_USERNAME") and os.getenv("MAIL_PASSWORD"))

if not EMAIL_ENABLED:
    logger.warning("Email service not configured. Set MAIL_USERNAME and MAIL_PASSWORD in .env to enable email notifications.")

fm = FastMail(conf) if EMAIL_ENABLED else None


async def send_welcome_email(
    email: EmailStr,
    first_name: str,
    last_name: str,
    temporary_password: str,
    login_url: str = None
) -> bool:
    """
    Send welcome email to newly created user with temporary password

    Args:
        email: User's email address
        first_name: User's first name
        last_name: User's last name
        temporary_password: Temporary password for first login
        login_url: URL to login page (optional)

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not EMAIL_ENABLED or not fm:
        logger.warning(f"Email not sent to {email} - email service not configured")
        return False

    try:
        # Default login URL if not provided
        if not login_url:
            login_url = os.getenv("FRONTEND_URL", "http://localhost:3000") + "/login"

        # HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #2196F3;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .credentials {{
                    background-color: white;
                    padding: 15px;
                    border-left: 4px solid #2196F3;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #2196F3;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to the Learning Platform!</h1>
                </div>
                <div class="content">
                    <p>Hello {first_name} {last_name},</p>

                    <p>Your account has been created. Below are your login credentials:</p>

                    <div class="credentials">
                        <p><strong>Email:</strong> {email}</p>
                        <p><strong>Temporary Password:</strong> {temporary_password}</p>
                    </div>

                    <p><strong>Important:</strong> You will be required to change your password on your first login for security purposes.</p>

                    <a href="{login_url}" class="button">Login Now</a>

                    <div class="footer">
                        <p>If you did not expect this email, please contact your administrator.</p>
                        <p>This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # Plain text alternative
        text_body = f"""
        Welcome to the Learning Platform!

        Hello {first_name} {last_name},

        Your account has been created. Below are your login credentials:

        Email: {email}
        Temporary Password: {temporary_password}

        IMPORTANT: You will be required to change your password on your first login for security purposes.

        Login at: {login_url}

        If you did not expect this email, please contact your administrator.
        This is an automated message, please do not reply to this email.
        """

        message = MessageSchema(
            subject="Welcome to the Learning Platform - Your Account Details",
            recipients=[email],
            body=text_body,
            html=html_body,
            subtype=MessageType.html
        )

        await fm.send_message(message)
        logger.info(f"Welcome email sent successfully to {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {e}")
        return False


async def send_password_reset_email(
    email: EmailStr,
    reset_token: str,
    reset_url: str = None
) -> bool:
    """
    Send password reset email with reset link

    Args:
        email: User's email address
        reset_token: Password reset token
        reset_url: URL to password reset page (optional)

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not EMAIL_ENABLED or not fm:
        logger.warning(f"Email not sent to {email} - email service not configured")
        return False

    try:
        # Default reset URL if not provided
        if not reset_url:
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            reset_url = f"{frontend_url}/reset-password?token={reset_token}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #f44336;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #f44336;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hello,</p>

                    <p>We received a request to reset your password. Click the button below to set a new password:</p>

                    <a href="{reset_url}" class="button">Reset Password</a>

                    <p style="margin-top: 20px;">Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #2196F3;">{reset_url}</p>

                    <p style="margin-top: 20px;"><strong>This link will expire in 24 hours.</strong></p>

                    <div class="footer">
                        <p>If you did not request a password reset, please ignore this email or contact support if you have concerns.</p>
                        <p>This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Password Reset Request

        Hello,

        We received a request to reset your password. Click the link below to set a new password:

        {reset_url}

        This link will expire in 24 hours.

        If you did not request a password reset, please ignore this email or contact support if you have concerns.
        This is an automated message, please do not reply to this email.
        """

        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email],
            body=text_body,
            html=html_body,
            subtype=MessageType.html
        )

        await fm.send_message(message)
        logger.info(f"Password reset email sent successfully to {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {e}")
        return False
