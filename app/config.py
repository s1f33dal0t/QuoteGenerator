import os
from dotenv import load_dotenv

load_dotenv()

COMPANY_NAME = os.getenv("COMPANY_NAME", "My Company Ltd")
COMPANY_ADDRESS = os.getenv("COMPANY_ADDRESS", "Address not set")
COMPANY_PHONE = os.getenv("COMPANY_PHONE", "")
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL", "")
COMPANY_ORG_NUMBER = os.getenv("COMPANY_ORG_NUMBER", "")
COMPANY_WEBSITE = os.getenv("COMPANY_WEBSITE", "")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "") or SMTP_USER

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
