import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")


class Config:
    """Application configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # Storage directories (relative to backend/)
    BACKEND_DIR = Path(__file__).resolve().parents[2]
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BACKEND_DIR / "uploads"))
    MERGED_DIR = Path(os.getenv("MERGED_DIR", BACKEND_DIR / "merged"))
    REPORT_DIR = Path(os.getenv("REPORT_DIR", BACKEND_DIR / "reports"))
    DATA_DIR = Path(os.getenv("DATA_DIR", BACKEND_DIR / "data"))

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50")) * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf"}

    # n8n integration
    N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://localhost:5678")
    N8N_EVALUATION_WEBHOOK = os.getenv(
        "N8N_EVALUATION_WEBHOOK",
        "/webhook/93f97adb-c532-44d9-9942-da74472c8cb6",
    )
    N8N_UDYAM_WEBHOOK = os.getenv("N8N_UDYAM_WEBHOOK", "/webhook/YOUR_UDYAM_WEBHOOK_ID")

    # Google
    GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "")
    GOOGLE_SHEETS_URL = os.getenv(
        "GOOGLE_SHEETS_URL",
        "https://docs.google.com/spreadsheets/d/1wkYCypcvEWqS1Uz-zOfoIpR9gdNjDoktTm50jc-eTL0/edit?usp=sharing",
    )
    GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "")

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Udyam / Selenium / OCR
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", "")
    CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "")
    UDYAM_INPUT_EXCEL = os.getenv("UDYAM_INPUT_EXCEL", str(DATA_DIR / "N8N.xlsx"))
    UDYAM_OUTPUT_EXCEL = os.getenv("UDYAM_OUTPUT_EXCEL", str(DATA_DIR / "scraped_output.xlsx"))
    UDYAM_COLUMN = os.getenv("UDYAM_COLUMN", "udyam registration")
    UDYAM_PORTAL_URL = os.getenv(
        "UDYAM_PORTAL_URL",
        "https://udyamregistration.gov.in/Government-India/Ministry-MSME-registration.htm",
    )
    MAX_CAPTCHA_ATTEMPTS = int(os.getenv("MAX_CAPTCHA_ATTEMPTS", "50"))

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

    @classmethod
    def ensure_directories(cls) -> None:
        for directory in (cls.UPLOAD_DIR, cls.MERGED_DIR, cls.REPORT_DIR, cls.DATA_DIR):
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def evaluation_webhook_url(cls) -> str:
        return f"{cls.N8N_BASE_URL.rstrip('/')}{cls.N8N_EVALUATION_WEBHOOK}"

    @classmethod
    def udyam_webhook_url(cls) -> str:
        return f"{cls.N8N_BASE_URL.rstrip('/')}{cls.N8N_UDYAM_WEBHOOK}"
