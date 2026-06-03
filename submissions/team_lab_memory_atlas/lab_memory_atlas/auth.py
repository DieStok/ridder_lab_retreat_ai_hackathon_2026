from __future__ import annotations

import hashlib
import secrets


PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 180_000


def hash_password(password: str) -> str:
    password = password.strip()
    if not password:
        raise ValueError("Password cannot be empty")
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), PASSWORD_ITERATIONS)
    return f"{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, encoded: str | None) -> bool:
    if not encoded:
        return False
    try:
        scheme, iterations, salt, expected = encoded.split("$", 3)
        if scheme != PASSWORD_SCHEME:
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.strip().encode("utf-8"), salt.encode("utf-8"), int(iterations))
    except (TypeError, ValueError):
        return False
    return secrets.compare_digest(digest.hex(), expected)
