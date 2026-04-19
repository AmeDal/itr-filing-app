import logging
import re
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
logger = logging.getLogger(__name__)


def now_ist():
    """Returns the current time in IST."""
    return datetime.now(IST)


def mask_uri(uri: str) -> str:
    """
    Masks credentials in a MongoDB URI or any standard connection string.
    Example: mongodb+srv://user:pass@host -> mongodb+srv://****:****@host
    """
    if not uri:
        return ""

    return re.sub(r'://([^:]+):([^@]+)@', r'://****:****@', uri)


def mask_pii(value: str, visible_chars: int = 4) -> str:
    """Masks all but the last visible_chars of a string."""
    if not value:
        return ""
    s = str(value)
    if len(s) <= visible_chars:
        return s
    return "*" * (len(s) - visible_chars) + s[-visible_chars:]


def mask_email(email: str) -> str:
    """Masks an email address for logging."""
    if not email or "@" not in email:
        return email
    parts = email.split("@")
    name = parts[0]
    domain = parts[1]
    if len(name) <= 1:
        return "*" + "@" + domain
    return name[0] + "*" * (len(name) - 1) + "@" + domain


def map_error_to_friendly_message(error: Exception) -> str:
    """
    Maps technical exceptions (like API errors) to user-friendly strings.
    """
    err_str = str(error)

    if "password protected" in err_str.lower() or "encrypted" in err_str.lower():
        return "PDF_PASSWORD_REQUIRED"

    if "503" in err_str and "UNAVAILABLE" in err_str:
        return "The AI engine is currently experiencing high demand. Please try again in a few moments."

    if "429" in err_str:
        return "Too many requests. Please wait a minute before retrying."

    if "400" in err_str:
        return "The document format or content couldn't be processed. Please ensure it's a clear image or PDF."

    if "401" in err_str or "403" in err_str:
        return "Internal authentication issue. Please contact support."

    if "{" in err_str or "code:" in err_str or "Error" in err_str:
        return "An unexpected error occurred while analyzing this document. Please re-upload or try again later."

    return err_str
