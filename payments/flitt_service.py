import hashlib
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def generate_flitt_signature(params: dict, secret_key: str = None) -> str:
    """
    Generate SHA1 signature for Flitt request or response parameters.
    Rules:
    - Exclude 'signature' and 'response_signature_string'
    - Exclude parameters that are None or empty string ''
    - Retain 0 or '0'
    - Sort keys alphabetically
    - Prepend secret_key, join with '|'
    - Compute sha1 lowercase hex digest
    """
    secret = secret_key or getattr(settings, 'FLITT_SECRET_KEY', 'test')

    data = [secret]
    # Filter and sort keys
    valid_keys = [
        k for k in sorted(params.keys())
        if k not in ('signature', 'response_signature_string')
        and params[k] is not None
        and params[k] != ''
    ]

    for k in valid_keys:
        val = params[k]
        if isinstance(val, (dict, list)):
            # If nested, serialize or omit based on top-level signature requirement
            continue
        data.append(str(val))

    sign_string = "|".join(data)
    return hashlib.sha1(sign_string.encode('utf-8')).hexdigest().lower()


def verify_flitt_signature(params: dict, secret_key: str = None) -> bool:
    """
    Validate the signature received in a callback or response from Flitt.
    """
    received_signature = params.get('signature', '')
    if not received_signature:
        return False

    expected_signature = generate_flitt_signature(params, secret_key=secret_key)
    return received_signature.lower() == expected_signature.lower()


class FlittPaymentClient:
    def __init__(self, merchant_id: int = None, secret_key: str = None, api_url: str = None):
        self.merchant_id = merchant_id or getattr(settings, 'FLITT_MERCHANT_ID', 1549901)
        self.secret_key = secret_key or getattr(settings, 'FLITT_SECRET_KEY', 'test')
        self.api_url = api_url or getattr(settings, 'FLITT_CHECKOUT_URL', 'https://pay.flitt.com/api/checkout/url')

    def create_checkout_session(
        self,
        order_id: str,
        amount_tetri: int,
        order_desc: str,
        server_callback_url: str,
        response_url: str,
        currency: str = "GEL",
        is_subscription: bool = False,
        sender_email: str = None,
        recurring_data: dict = None,
    ) -> dict:
        """
        Create a Flitt hosted checkout order.
        Returns dict with response_status and checkout_url (or error_message).
        """
        request_params = {
            "merchant_id": self.merchant_id,
            "order_id": order_id,
            "amount": amount_tetri,
            "currency": currency,
            "order_desc": order_desc,
            "server_callback_url": server_callback_url,
            "response_url": response_url,
        }

        if sender_email:
            request_params["sender_email"] = sender_email

        if is_subscription:
            request_params["subscription"] = "Y"
            # Default monthly recurring configuration if not provided
            request_params["recurring_data"] = recurring_data or {
                "every": 1,
                "period": "month",
                "amount": amount_tetri,
                "state": "shown_readonly",
                "readonly": "Y",
            }

        # Calculate signature from base scalar parameters
        signature = generate_flitt_signature(request_params, secret_key=self.secret_key)
        request_params["signature"] = signature

        payload = {"request": request_params}

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=20,
            )
            response.raise_for_status()
            res_json = response.json()
            return res_json.get("response", {})
        except requests.RequestException as exc:
            logger.error("Flitt API connection error for order %s: %s", order_id, exc)
            return {
                "response_status": "failure",
                "error_message": f"Flitt API connection failed: {str(exc)}",
                "error_code": "CONNECTION_ERROR",
            }
