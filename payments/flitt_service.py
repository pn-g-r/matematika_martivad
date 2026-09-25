import base64
import hashlib
import hmac
import json
import logging
import urllib.parse
from datetime import datetime

import requests
from django.conf import settings
from flittpayments import Api, Checkout

logger = logging.getLogger(__name__)

# Monthly subscription runs for 12 charges (= 1 year), then stops at Flitt.
SUBSCRIPTION_MONTHLY_CHARGE_COUNT = 12
FLITT_REQUEST_TIMEOUT_SECONDS = 5

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
    valid_keys = [
        k for k in sorted(params.keys())
        if k not in ('signature', 'response_signature_string')
        and params[k] is not None
        and params[k] != ''
    ]

    for k in valid_keys:
        val = params[k]
        if isinstance(val, (dict, list)):
            continue
        data.append(str(val))

    sign_string = "|".join(data)
    return hashlib.sha1(sign_string.encode('utf-8')).hexdigest().lower()


def parse_flitt_subscription_data(data_field):
    """Parse subscription checkout `data` from SDK (JSON string or dict)."""
    if isinstance(data_field, dict):
        return data_field
    if isinstance(data_field, str):
        return json.loads(data_field)
    raise TypeError(f"Unexpected Flitt subscription data type: {type(data_field)}")


def is_flitt_subscription_stopped(res: dict) -> bool:
    """
    True only when Flitt reports the subscription schedule is actually stopped.
    response_status=success means the API request was accepted, not that billing stopped.
    """
    if not isinstance(res, dict):
        return False
    status = (res.get('status') or '').lower()
    return status in ('disabled', 'canceled')


def verify_flitt_signature(params: dict, secret_key: str = None) -> bool:
    """
    Validate the signature received in a callback or response from Flitt.
    """
    received_signature = params.get('signature', '')
    if not received_signature:
        return False

    expected_signature = generate_flitt_signature(params, secret_key=secret_key)
    return hmac.compare_digest(received_signature.lower(), expected_signature.lower())


class FlittPaymentClient:
    def __init__(self, merchant_id: int = None, secret_key: str = None):
        self.merchant_id = merchant_id or getattr(settings, 'FLITT_MERCHANT_ID', 1549901)
        self.secret_key = secret_key or getattr(settings, 'FLITT_SECRET_KEY', 'test')

    def create_checkout_session(
        self,
        order_id: str,
        amount_tetri: int,
        order_desc: str,
        server_callback_url: str,
        response_url: str,
        currency: str = "GEL",
        is_subscription: bool = False,
        subscription_callback_url: str = None,
        sender_email: str = None,
        recurring_data: dict = None,
        lang: str = None,
    ) -> dict:
        """
        Create a Flitt hosted checkout order for one-time payments (v1.0)
        or subscription payments (v2.0).
        Returns a dict with 'response_status', 'checkout_url', and 'payment_id'.
        """
        try:
            if is_subscription:
                api = Api(
                    merchant_id=self.merchant_id,
                    secret_key=self.secret_key,
                    api_protocol='2.0',
                    timeout=FLITT_REQUEST_TIMEOUT_SECONDS,
                )
                checkout = Checkout(api=api)

                # flittpayments 3.0.0 requires start_time even though Flitt's API docs allow omitting it.
                rec_payload = recurring_data or {
                    "start_time": datetime.now().strftime('%Y-%m-%d'),
                    "every": 1,
                    "period": "month",
                    "amount": amount_tetri,
                    "quantity": SUBSCRIPTION_MONTHLY_CHARGE_COUNT,
                    "readonly": "y",
                    "state": "shown_readonly",
                }

                checkout_lang = lang or getattr(settings, 'FLITT_CHECKOUT_LANG', 'ka')
                sub_data = {
                    "order_id": order_id,
                    "amount": amount_tetri,
                    "currency": currency,
                    "order_desc": order_desc,
                    "response_url": response_url,
                    "server_callback_url": server_callback_url,
                    "subscription_callback_url": subscription_callback_url or server_callback_url,
                    "recurring_data": rec_payload,
                    "lang": checkout_lang,
                }
                if sender_email:
                    sub_data["sender_email"] = sender_email

                res = checkout.subscription(sub_data)

                checkout_url = ""
                payment_id = ""
                payment_token = ""
                if isinstance(res, dict):
                    if "data" in res:
                        try:
                            parsed_data = parse_flitt_subscription_data(res["data"])
                            order_dict = parsed_data.get("order", parsed_data)
                            checkout_url = order_dict.get("checkout_url", "")
                            payment_id = str(order_dict.get("payment_id", ""))
                            payment_token = order_dict.get("token", "")
                        except Exception as parse_err:
                            logger.error("Failed to parse Flitt subscription response data: %s", parse_err)
                    elif "checkout_url" in res:
                        checkout_url = res["checkout_url"]
                        payment_id = str(res.get("payment_id", ""))
                        payment_token = str(res.get("token", ""))

                if checkout_url and not payment_token:
                    qs = urllib.parse.parse_qs(urllib.parse.urlparse(checkout_url).query)
                    payment_token = qs.get("token", [""])[0]

                if checkout_url:
                    return {
                        "response_status": "success",
                        "checkout_url": checkout_url,
                        "payment_id": payment_id,
                        "payment_token": payment_token,
                        "raw": res,
                    }
                else:
                    return {
                        "response_status": "failure",
                        "error_message": "Checkout URL not found in Flitt response",
                        "raw": res,
                    }
            else:
                api = Api(
                    merchant_id=self.merchant_id,
                    secret_key=self.secret_key,
                    api_protocol='1.0',
                    timeout=FLITT_REQUEST_TIMEOUT_SECONDS,
                )
                checkout = Checkout(api=api)

                checkout_lang = lang or getattr(settings, 'FLITT_CHECKOUT_LANG', 'ka')
                order_data = {
                    "order_id": order_id,
                    "amount": amount_tetri,
                    "currency": currency,
                    "order_desc": order_desc,
                    "response_url": response_url,
                    "server_callback_url": server_callback_url,
                    "lang": checkout_lang,
                }
                if sender_email:
                    order_data["sender_email"] = sender_email

                res = checkout.url(order_data)

                checkout_url = res.get("checkout_url", "")
                payment_id = str(res.get("payment_id", ""))
                payment_token = res.get("token", "")
                if checkout_url and not payment_token:
                    qs = urllib.parse.parse_qs(urllib.parse.urlparse(checkout_url).query)
                    payment_token = qs.get("token", [""])[0]

                response_status = res.get("response_status", "success" if checkout_url else "failure")

                if checkout_url:
                    return {
                        "response_status": "success",
                        "checkout_url": checkout_url,
                        "payment_id": payment_id,
                        "payment_token": payment_token,
                        "raw": res,
                    }
                else:
                    return {
                        "response_status": response_status,
                        "error_message": res.get("error_message", "Failed to create checkout URL"),
                        "raw": res,
                    }

        except requests.exceptions.Timeout:
            logger.warning('Flitt checkout request timed out for order %s', order_id)
            return {
                'response_status': 'failure',
                'error_message': 'Flitt did not respond in time. Please try again later.',
                'error_code': 'TIMEOUT',
            }
        except Exception as exc:
            logger.exception("Flitt API error for order %s: %s", order_id, exc)
            return {
                "response_status": "failure",
                "error_message": str(exc),
                "error_code": "EXCEPTION",
            }

    def get_order_status(self, order_id: str) -> dict:
        """
        Query current order status from Flitt API.
        """
        data = {
            'order_id': order_id,
            'merchant_id': self.merchant_id,
            'version': '1.0.1',
        }
        data['signature'] = generate_flitt_signature(data, secret_key=self.secret_key)
        try:
            resp = requests.post('https://pay.flitt.com/api/status/order_id', json={'request': data}, timeout=FLITT_REQUEST_TIMEOUT_SECONDS)
            resp.raise_for_status()
            res_json = resp.json()
            if isinstance(res_json, dict) and isinstance(res_json.get('response'), dict):
                res_data = res_json['response']
                if res_data.get('version') == '2.0':
                    encoded = res_data.get('data')
                    received = res_data.get('signature')
                    if not isinstance(encoded, str) or not isinstance(received, str):
                        logger.warning('Ignoring incomplete Flitt v2 status response for order %s', order_id)
                        return {}
                    expected = hashlib.sha1(f'{self.secret_key}|{encoded}'.encode('utf-8')).hexdigest()
                    if not hmac.compare_digest(received.lower(), expected):
                        logger.warning('Ignoring invalid Flitt v2 status signature for order %s', order_id)
                        return {}
                    try:
                        decoded = json.loads(base64.b64decode(encoded, validate=True).decode('utf-8'))
                        status_info = decoded['order']
                    except (ValueError, KeyError, TypeError) as decode_err:
                        logger.warning('Failed to decode Flitt v2 status for order %s: %s', order_id, decode_err)
                        return {}
                    if not isinstance(status_info, dict):
                        return {}
                elif verify_flitt_signature(res_data, secret_key=self.secret_key):
                    status_info = res_data
                else:
                    logger.warning('Ignoring unsigned or invalid Flitt status response for order %s', order_id)
                    return {}
                if (str(status_info.get('order_id', '')) != order_id
                        or str(status_info.get('merchant_id', '')) != str(self.merchant_id)):
                    logger.warning('Ignoring mismatched Flitt status response for order %s', order_id)
                    return {}
                return status_info
            logger.warning('Ignoring unexpected Flitt status response for order %s', order_id)
            return {}
        except Exception as e:
            logger.error("Failed to query Flitt order status for %s: %s", order_id, e)
            return {}

    def cancel_subscription(self, order_id: str) -> dict:
        """
        Cancel / stop an active recurring subscription in Flitt (v2.0).
        """
        try:
            api = Api(
                merchant_id=self.merchant_id,
                secret_key=self.secret_key,
                api_protocol='2.0',
                timeout=FLITT_REQUEST_TIMEOUT_SECONDS,
            )
            checkout = Checkout(api=api)
            res = checkout.subscription_stop(order_id=order_id)
            if isinstance(res, dict):
                return {
                    "response_status": res.get('response_status', ''),
                    "status": res.get('status', ''),
                    "raw": res,
                }
            return {
                "response_status": getattr(res, 'response_status', '') or '',
                "status": getattr(res, 'status', '') or '',
                "raw": str(res),
            }
        except requests.exceptions.Timeout:
            logger.warning('Flitt subscription stop timed out for order %s', order_id)
            return {'response_status': 'failure', 'error_message': 'Flitt did not respond in time.'}
        except Exception as exc:
            logger.warning("Flitt SDK subscription_stop exception for %s: %s. Trying direct API call.", order_id, exc)
            data = {
                'order_id': order_id,
                'merchant_id': self.merchant_id,
                'action': 'stop',
            }
            data['signature'] = generate_flitt_signature(data, secret_key=self.secret_key)
            try:
                resp = requests.post('https://pay.flitt.com/api/subscription', json={'request': data}, timeout=FLITT_REQUEST_TIMEOUT_SECONDS)
                res_json = resp.json()
                if 'response' in res_json:
                    return res_json['response']
                return res_json
            except Exception as direct_err:
                logger.exception("Failed to stop Flitt subscription for %s: %s", order_id, direct_err)
                return {
                    "response_status": "failure",
                    "error_message": str(direct_err),
                }

