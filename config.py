import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'database' / 'helpdesk.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024
    WTF_CSRF_ENABLED = True
