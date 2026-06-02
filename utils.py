import base64
import hmac
import hashlib
import json
import time
import secrets
import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")


# ========================
# BASE64 HELPERS
# ========================
def b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def b64_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


# ========================
# GENERATE TOKEN
# ========================
def generate_token(staff_id: str, tkv: str, expiry_seconds=86400):
    payload = {
        "staff_id": staff_id,
        "tkv": tkv,
        "exp": int(time.time()) + expiry_seconds,
        "iat": int(time.time()),
        "nonce": secrets.token_hex(8)
    }

    payload_json = json.dumps(payload, separators=(",", ":")).encode()
    payload_b64 = b64_encode(payload_json)

    signature = hmac.new(
        SECRET_KEY.encode(),
        payload_b64.encode(),
        hashlib.sha256
    ).hexdigest()

    return f"{payload_b64}::{signature}"


# ========================
# VERIFY TOKEN (BOOLEAN STYLE)
# ========================
def verify_token(staff_id: str, tkv: str, token: str) -> bool:
    try:
        payload_b64, signature = token.split("::")

        expected_sig = hmac.new(
            SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()

        # signature check
        if not hmac.compare_digest(signature, expected_sig):
            return False

        payload_json = b64_decode(payload_b64)
        payload = json.loads(payload_json)

        # expiry check
        if payload.get("exp", 0) < int(time.time()):
            return False

        # 🔥 match staff id
        if payload.get("staff_id") != staff_id:
            return False

        # 🔥 match token version
        if payload.get("tkv") != tkv:
            return False

        return True

    except Exception:
        return False