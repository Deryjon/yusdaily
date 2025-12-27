import hashlib
import hmac
import json
from typing import Any
from urllib.parse import parse_qsl


def verify_init_data(init_data: str, bot_token: str) -> tuple[bool, dict[str, Any] | str]:
    params = dict(parse_qsl(init_data, strict_parsing=True))
    received_hash = params.pop("hash", None)
    if not received_hash:
        return False, "missing hash"

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(params.items()))
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(calculated_hash, received_hash):
        return False, "invalid hash"

    user_payload = None
    if "user" in params:
        try:
            user_payload = json.loads(params["user"])
        except json.JSONDecodeError:
            return False, "invalid user payload"

    result = dict(params)
    if user_payload is not None:
        result["user"] = user_payload

    return True, result
