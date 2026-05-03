import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
IS_VERCEL = bool(os.environ.get("VERCEL"))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:////tmp/helpdesk.db" if IS_VERCEL else f"sqlite:///{BASE_DIR / 'database' / 'helpdesk.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = Path("/tmp/resolveit-uploads") if IS_VERCEL else BASE_DIR / "static" / "uploads"
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024
    WTF_CSRF_ENABLED = True
    
    # Security Configuration
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Mail configuration
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@resolveit.com")
