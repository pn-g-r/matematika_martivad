import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import RegistrationOTP
from .sms import send_registration_otp_sms

OTP_LENGTH = 6
SESSION_REGISTRATION_DATA = "registration_pending_data"
SESSION_REGISTRATION_PHONE = "registration_pending_phone"


def otp_expiry_seconds():
    return int(getattr(settings, "REGISTRATION_OTP_EXPIRY_SECONDS", 600))


def otp_resend_seconds():
    return int(getattr(settings, "REGISTRATION_OTP_RESEND_SECONDS", 60))


def otp_max_attempts():
    return int(getattr(settings, "REGISTRATION_OTP_MAX_ATTEMPTS", 5))


def hash_otp(phone, code):
    return hmac.new(
        settings.SECRET_KEY.encode(),
        f"{phone}:{code}".encode(),
        hashlib.sha256,
    ).hexdigest()


def generate_otp():
    return f"{secrets.randbelow(10 ** OTP_LENGTH):0{OTP_LENGTH}d}"


def mask_phone(phone):
    if not phone or len(phone) < 6:
        return phone
    return f"{phone[:3]}***{phone[-3:]}"


def clear_registration_session(request):
    for key in (SESSION_REGISTRATION_DATA, SESSION_REGISTRATION_PHONE):
        request.session.pop(key, None)


def request_registration_otp(phone):
    now = timezone.now()
    latest = RegistrationOTP.objects.filter(phone_number=phone).first()
    if latest:
        elapsed = (now - latest.created_at).total_seconds()
        wait = otp_resend_seconds() - int(elapsed)
        if wait > 0:
            return False, f"გთხოვთ დაელოდოთ {wait} წამი, სანამ კოდს ხელახლა გამოაგზავნით."

    code = generate_otp()
    RegistrationOTP.objects.filter(phone_number=phone, is_used=False).update(is_used=True)
    otp = RegistrationOTP.objects.create(
        phone_number=phone,
        code_hash=hash_otp(phone, code),
        expires_at=now + timedelta(seconds=otp_expiry_seconds()),
    )
    ok, err = send_registration_otp_sms(phone, code)
    if not ok:
        otp.delete()
        return False, err
    return True, None


def verify_registration_otp(phone, code):
    now = timezone.now()
    otp = (
        RegistrationOTP.objects.filter(
            phone_number=phone,
            is_used=False,
            expires_at__gt=now,
        )
        .order_by("-created_at")
        .first()
    )
    if otp is None:
        return False, "კოდი არასწორია ან ვადაგასულია."
    if otp.attempts >= otp_max_attempts():
        return False, "ძალიან ბევრი მცდელობა. მოითხოვეთ ახალი კოდი."

    otp.attempts += 1
    expected = hash_otp(phone, code.strip())
    if not hmac.compare_digest(otp.code_hash, expected):
        otp.save(update_fields=["attempts"])
        return False, "კოდი არასწორია."

    otp.is_used = True
    otp.save(update_fields=["attempts", "is_used"])
    return True, None
