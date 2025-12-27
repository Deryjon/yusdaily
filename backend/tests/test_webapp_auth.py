import hashlib
import hmac
import json
import unittest
from urllib.parse import urlencode

from app.services.webapp_auth import verify_init_data


class WebAppAuthTests(unittest.TestCase):
    def test_verify_init_data_valid(self) -> None:
        bot_token = "test:token"
        user_payload = {"id": 123, "username": "tester"}
        params = {
            "auth_date": "1700000000",
            "query_id": "AAE111",
            "user": json.dumps(user_payload, separators=(",", ":")),
        }

        data_check_string = "\n".join(
            f"{key}={value}" for key, value in sorted(params.items())
        )
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        params["hash"] = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        init_data = urlencode(params)
        ok, result = verify_init_data(init_data, bot_token)

        self.assertTrue(ok)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("user"), user_payload)


if __name__ == "__main__":
    unittest.main()
