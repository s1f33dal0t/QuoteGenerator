"""Send quotes by email via SMTP."""
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from app import config


class EmailError(Exception):
    pass


def send_quote_email(
    to_email: str,
    customer_name: str,
    quote_number: str,
    quote_title: str,
    pdf_bytes: bytes,
) -> None:
    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        raise EmailError(
            "Email settings are missing. Configure SMTP_USER and SMTP_PASSWORD in the .env file."
        )

    msg = MIMEMultipart("mixed")
    msg["From"] = f"{config.COMPANY_NAME} <{config.FROM_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = f"Quote {quote_number} - {quote_title}"

    body = f"""Hi {customer_name},

Thank you for your interest. Please find attached our quote {quote_number} for "{quote_title}".

Feel free to reach out if you have any questions.

Best regards,
{config.COMPANY_NAME}
{config.COMPANY_PHONE}
{config.COMPANY_EMAIL}
"""
    msg.attach(MIMEText(body, "plain", "utf-8"))

    attachment = MIMEBase("application", "pdf")
    attachment.set_payload(pdf_bytes)
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        f'attachment; filename="Quote-{quote_number}.pdf"',
    )
    msg.attach(attachment)

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.FROM_EMAIL, to_email, msg.as_string())
    except smtplib.SMTPAuthenticationError:
        raise EmailError("Authentication failed. Check SMTP_USER and SMTP_PASSWORD.")
    except smtplib.SMTPException as exc:
        raise EmailError(f"SMTP error: {exc}")
    except UnicodeError as exc:
        raise EmailError(
            "Invalid characters in SMTP credentials. Use ASCII-only SMTP_USER and SMTP_PASSWORD."
        )
    except OSError as exc:
        raise EmailError(f"Network error: {exc}")
    except Exception as exc:
        raise EmailError(f"Unknown email error: {exc}")
