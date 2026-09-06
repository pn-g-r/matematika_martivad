"""
Manual renewal simulation — posts a signed fake Flitt webhook locally (no ngrok).
Run: python manage.py shell < scripts/manual_renewal_test.py
Or:  python scripts/manual_renewal_test.py (from project root with DJANGO_SETTINGS_MODULE)
"""
import os
import sys
from datetime import timedelta
from decimal import Decimal

import django

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
    django.setup()

from django.test import Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from courses.models import Course
from payments.models import PaymentOrder, UserCourseAccess, PlanType, OrderStatus
from payments.flitt_service import generate_flitt_signature

User = get_user_model()


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    section("SETUP: user, course, approved parent subscription order")
    course, _ = Course.objects.get_or_create(
        title="Manual Renewal Test Course",
        defaults={
            "grade": "IX",
            "short_description": "test",
            "long_description": "test",
            "instructor_name": "Test",
            "duration": "10h",
            "lessons_count": 1,
            "video_url": "https://youtube.com/embed/test",
            "price": Decimal("50.00"),
        },
    )
    user, _ = User.objects.get_or_create(
        username="manual_renewal_test_user",
        defaults={
            "phone_number": "599000001",
            "student_name": "Renewal Tester",
            "parent_name": "Parent",
            "grade": "IX",
            "book_author": "Test",
        },
    )
    if not user.has_usable_password():
        user.set_password("TestPass123!@#")
        user.save()

    parent_order_id = "MM_MANUAL_PARENT_RENEWAL_001"
    PaymentOrder.objects.filter(order_id=parent_order_id).delete()
    PaymentOrder.objects.filter(order_id="MM_MANUAL_CHILD_RENEWAL_002").delete()
    UserCourseAccess.objects.filter(user=user, course=course).delete()

    parent = PaymentOrder.objects.create(
        order_id=parent_order_id,
        user=user,
        course=course,
        plan_type=PlanType.MONTHLY,
        amount_gel=Decimal("50.00"),
        amount_tetri=5000,
        currency="GEL",
        order_desc="Manual test parent subscription",
        is_subscription=True,
        status=OrderStatus.APPROVED,
        flitt_payment_id="111111111",
    )

    initial_expiry = timezone.now() + timedelta(days=5)
    access = UserCourseAccess.objects.create(
        user=user,
        course=course,
        plan_type=PlanType.MONTHLY,
        is_active=True,
        auto_renew=True,
        starts_at=timezone.now() - timedelta(days=25),
        expires_at=initial_expiry,
        last_order=parent,
        subscription_order_id=parent_order_id,
    )
    parent.access_granted_at = timezone.now()
    parent.fulfilled_payment_id = "111111111"
    parent.save(update_fields=["access_granted_at", "fulfilled_payment_id"])

    print(f"Parent order: {parent.order_id} [{parent.status}]")
    print(f"Access expires_at BEFORE renewal: {access.expires_at.isoformat()}")

    section("STEP 1: Simulate month-2 renewal webhook (signed POST to /payments/callback/)")
    client = Client()
    renewal_params = {
        "order_id": "MM_MANUAL_CHILD_RENEWAL_002",
        "parent_order_id": parent_order_id,
        "merchant_id": 1549901,
        "amount": "5000",
        "currency": "GEL",
        "order_status": "approved",
        "response_status": "success",
        "payment_id": 222222222,
    }
    renewal_params["signature"] = generate_flitt_signature(renewal_params, secret_key="test")

    response = client.post(
        reverse("payments:flitt_callback"),
        data=renewal_params,
        content_type="application/json",
        HTTP_HOST="127.0.0.1",
    )
    print(f"HTTP status: {response.status_code}")
    print(f"Response body: {response.content.decode()}")

    section("RESULTS")
    child = PaymentOrder.objects.filter(order_id="MM_MANUAL_CHILD_RENEWAL_002").first()
    access.refresh_from_db()

    checks = []
    checks.append(("Callback returned 200", response.status_code == 200))
    checks.append(("Child renewal order created", child is not None))
    if child:
        checks.append(("Child order approved", child.status == OrderStatus.APPROVED))
        checks.append(("Child linked to same user/course", child.user_id == user.id and child.course_id == course.id))
        checks.append(("Child amount matches parent (5000 tetri)", child.amount_tetri == 5000))
    checks.append(("Access expires_at extended", access.expires_at > initial_expiry))
    if access.expires_at > initial_expiry:
        delta_days = (access.expires_at - initial_expiry).days
        checks.append(("Extension roughly 30 days", 28 <= delta_days <= 32))
    checks.append(("subscription_order_id unchanged (root)", access.subscription_order_id == parent_order_id))
    checks.append(("last_order points to renewal child", access.last_order_id == child.id if child else False))

    print(f"Access expires_at AFTER renewal:  {access.expires_at.isoformat()}")
    print(f"Extension: +{(access.expires_at - initial_expiry).days} days from pre-renewal expiry")
    if child:
        print(f"Child order: {child.order_id} [{child.status}] fulfilled_payment_id={child.fulfilled_payment_id!r}")

    section("PASS/FAIL SUMMARY")
    all_ok = True
    for label, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {label}")
        if not ok:
            all_ok = False

    section("STEP 2: Duplicate renewal webhook (idempotency)")
    response2 = client.post(
        reverse("payments:flitt_callback"),
        data=renewal_params,
        content_type="application/json",
        HTTP_HOST="127.0.0.1",
    )
    access.refresh_from_db()
    expiry_after_dup = access.expires_at
    print(f"Duplicate callback HTTP: {response2.status_code}")
    print(f"expires_at unchanged on duplicate: {expiry_after_dup == access.expires_at}")
    dup_ok = response2.status_code == 200 and expiry_after_dup == access.expires_at
    print(f"  [{'PASS' if dup_ok else 'FAIL'}] Duplicate renewal does not double-extend access")

    section("OVERALL")
    if all_ok and dup_ok:
        print("SUCCESS: Manual renewal simulation passed locally (no ngrok).")
        return 0
    print("FAILURE: One or more checks failed — see above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
