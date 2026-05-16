import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "b1df31b79189006c4ff166ebd786acf282f3b825f88345a38d6ab4b193be0f9f"
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:///macho_bank.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = True

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = False