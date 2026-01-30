from datetime import datetime, timedelta, timezone
import os

import jwt


def _get_secret() -> str:
    secret = os.getenv("JWT_SECRET", "")
    if not secret:
        raise RuntimeError("JWT_SECRET is required for auth tokens")
    return secret


def create_access_token(phone: str, expires_in_days: int = 30) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": phone,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=expires_in_days)).timestamp()),
    }
    return jwt.encode(payload, _get_secret(), algorithm="HS256")


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, _get_secret(), algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        return None
    return subject
