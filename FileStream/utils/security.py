import hmac
import time
import hashlib

from FileStream.config import Server


def generate_secure_token(file_id: str, expiry_seconds: int = None) -> str:
    """
    Builds a signed, expiring token for a given file_id.
    Format: "<expires_at>.<signature>"
    The signature is an HMAC-SHA256 of "file_id:expires_at", keyed with
    Server.SECRET_KEY, so a client cannot forge or extend a link without
    knowing the secret key.
    """
    if expiry_seconds is None:
        expiry_seconds = Server.LINK_EXPIRY_SECONDS

    expires_at = int(time.time()) + expiry_seconds
    payload = f"{file_id}:{expires_at}"
    signature = hmac.new(
        Server.SECRET_KEY.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()[:32]

    return f"{expires_at}.{signature}"


def verify_secure_token(file_id: str, token: str) -> bool:
    """
    Verifies a token produced by generate_secure_token.
    Returns True only if the signature matches AND the token hasn't expired.
    """
    if not token or "." not in token:
        return False

    expires_at_str, _, signature = token.partition(".")

    try:
        expires_at = int(expires_at_str)
    except ValueError:
        return False

    if time.time() > expires_at:
        return False

    payload = f"{file_id}:{expires_at}"
    expected_signature = hmac.new(
        Server.SECRET_KEY.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()[:32]

    return hmac.compare_digest(signature, expected_signature)
