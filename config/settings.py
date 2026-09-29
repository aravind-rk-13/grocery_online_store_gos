"""Single source for environment configuration (CODIFAi self-verification: one mechanism for creds/baseURL)."""
import os

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not set. Copy .env.example to .env and fill it in.")
    return value


APP_URL = os.getenv("APP_URL", "https://groceryapp.uniqassosiates.com/admin").rstrip("/")
LOGIN_URL = f"{APP_URL}/login"


def credentials() -> tuple[str, str]:
    """Return (username, password) from .env. Never log or print the result."""
    return _require("APP_USERNAME"), _require("APP_PASSWORD")
