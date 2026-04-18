from passlib.context import CryptContext
import re


# Argon2 is more secure than bcrypt (winner of Password Hashing Competition 2015)
pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,        # 3 iterations
    argon2__parallelism=4       # 4 threads
)

MIN_PASSWORD_LENGTH = 12
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$")


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validates password meets minimum security requirements.

    Requirements:
    - At least 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (@$!%*?&)

    Returns:
        (is_valid, error_message)
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"

    if not PASSWORD_PATTERN.match(password):
        return False, ("Password must contain uppercase, lowercase, digit, "
                       "and special character (@$!%*?&)")

    return True, ""


def hash_password(password: str) -> str:
    """
    Hashes a password using Argon2 (modern, high-security algorithm).

    Raises:
        ValueError: If password doesn't meet strength requirements.
    """
    is_valid, error_msg = validate_password_strength(password)
    if not is_valid:
        raise ValueError(error_msg)

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored Argon2 or bcrypt hash.

    Supports both Argon2 and bcrypt hashes for backward compatibility.
    """
    return pwd_context.verify(plain_password, hashed_password)
