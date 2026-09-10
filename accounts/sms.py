import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_sms(
    api_key,
    destination,
    sender,
    content,
    urgent=False,
    reference=None,
    content_type=None,
    scheduled_at=None,
    show_service_time=False,
):
    url = "https://smsoffice.ge/api/v2/send/"
    payload = {
        "key": api_key,
        "destination": destination,
        "sender": sender,
        "content": content,
    }
    if urgent:
        payload["urgent"] = "true"
    if reference:
        payload["reference"] = reference
    if content_type:
        payload["contentType"] = str(content_type)
    if scheduled_at:
        payload["scheduledAt"] = str(scheduled_at)
    if show_service_time:
        payload["showServiceTime"] = "true"
    response = requests.post(url, data=payload, timeout=15)
    return response.json()


def send_otp_sms(destination, otp_code):
    api_key = getattr(settings, "SMS_OFFICE_API_KEY", "") or ""
    sender = getattr(settings, "SMS_OFFICE_SENDER", "MatMartivad")
    if not api_key:
        logger.error("SMS_OFFICE_API_KEY is not configured")
        return False, "SMS სერვისი არ არის კონფიგურირებული."

    content = f"მათემატიკა მარტივად. პაროლის აღდგენის კოდი: {otp_code}"
    try:
        result = send_sms(
            api_key=api_key,
            destination=destination,
            sender=sender,
            content=content,
            urgent=True,
        )
    except (requests.RequestException, ValueError):
        logger.exception("Failed to send OTP SMS to %s", destination)
        return False, "SMS გაგზავნა ვერ მოხერხდა. სცადეთ თავიდან."

    if not isinstance(result, dict):
        logger.error("Unexpected SMS Office response: %s", result)
        return False, "SMS გაგზავნა ვერ მოხერხდა. სცადეთ თავიდან."

    success = result.get("Success") is True or result.get("ErrorCode") == 0
    if not success:
        logger.error("SMS Office rejected OTP send: %s", result)
        return False, "SMS გაგზავნა ვერ მოხერხდა. სცადეთ თავიდან."
    return True, None
