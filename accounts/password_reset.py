import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import CustomUser, PasswordResetOTP
from .sms import send_otp_sms

OTP_LENGTH = 6
SESSION_PHONE = "password_reset_phone"
SESSION_USER_ID = "password_reset_user_id"

GENERIC_OTP_SENT_MESSAGE = (
    "თუ ეს ნომერი რეგისტრირებულია, SMS კოდი გამოგეგზავნებათ."
)


def otp_expiry_seconds():
    return int(getattr(settings, "PASSWORD_RESET_OTP_EXPIRY_SECONDS", 600))


def otp_resend_seconds():
    return int(getattr(settings, "PASSWORD_RESET_OTP_RESEND_SECONDS", 60))


def otp_max_attempts():
    return int(getattr(settings, "PASSWORD_RESET_OTP_MAX_ATTEMPTS", 5))


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


def clear_password_reset_session(request):
    for key in (SESSION_PHONE, SESSION_USER_ID):
        request.session.pop(key, None)


def request_otp(phone):
    now = timezone.now()
    latest = PasswordResetOTP.objects.filter(phone_number=phone).first()
    if latest:
        elapsed = (now - latest.created_at).total_seconds()
        wait = otp_resend_seconds() - int(elapsed)
        if wait > 0:
            return False, f"გთხოვთ დაელოდოთ {wait} წამი, სანამ კოდს ხელახლა გამოაგზავნით."

    user = CustomUser.objects.filter(phone_number=phone, is_active=True).first()
    if not user:
        return True, None

    code = generate_otp()
    PasswordResetOTP.objects.filter(phone_number=phone, is_used=False).update(is_used=True)
    otp = PasswordResetOTP.objects.create(
        phone_number=phone,
        code_hash=hash_otp(phone, code),
        expires_at=now + timedelta(seconds=otp_expiry_seconds()),
    )
    ok, err = send_otp_sms(phone, code)
    if not ok:
        otp.delete()
        return False, err
    return True, None


def verify_otp(phone, code):
    now = timezone.now()
    otp = (
        PasswordResetOTP.objects.filter(
            phone_number=phone,
            is_used=False,
            expires_at__gt=now,
        )
        .order_by("-created_at")
        .first()
    )
    if otp is None:
        return None, "კოდი არასწორია ან ვადაგასულია."
    if otp.attempts >= otp_max_attempts():
        return None, "ძალიან ბევრი მცდელობა. მოითხოვეთ ახალი კოდი."

    otp.attempts += 1
    expected = hash_otp(phone, code.strip())
    if not hmac.compare_digest(otp.code_hash, expected):
        otp.save(update_fields=["attempts"])
        return None, "კოდი არასწორია."

    otp.is_used = True
    otp.save(update_fields=["attempts", "is_used"])
    user = CustomUser.objects.filter(phone_number=phone, is_active=True).first()
    if user is None:
        return None, "კოდი არასწორია ან ვადაგასულია."
    return user, None
