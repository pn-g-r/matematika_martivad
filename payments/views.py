import json
import logging
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from .models import PaymentOrder, UserCourseAccess, PlanType, OrderStatus
from courses.models import Course
from .flitt_service import FlittPaymentClient, verify_flitt_signature

logger = logging.getLogger(__name__)

PLANS_CONFIG = {
    PlanType.MONTHLY: {
        'title': 'ყოველთვიური გამოწერა',
        'subtitle': 'ავტომატური განახლება ყოველთვე',
        'price_gel': Decimal('50.00'),
        'price_tetri': 5000,
        'period_label': 'თვეში',
        'is_subscription': True,
        'description': 'მათემატიკა მარტივად - ყოველთვიური გამოწერა (50 ₾)',
        'badge': 'მოქნილი პაკეტი',
        'features': [
            'სრული წვდომა არჩეული კურსის მასალაზე',
            'ყველა ვიდეო-გაკვეთილი და ამოცანის ამოხსნა',
            'გაუქმება შესაძლებელია ნებისმიერ დროს',
        ],
    },
    PlanType.YEARLY: {
        'title': '1-წლიანი სრული პაკეტი',
        'subtitle': 'ერთჯერადი გადახდა 1 წლით',
        'price_gel': Decimal('400.00'),
        'price_tetri': 40000,
        'period_label': 'წელიწადში',
        'is_subscription': False,
        'description': 'მათემატიკა მარტივად - 1-წლიანი წვდომა (400 ₾)',
        'badge': 'დაზოგეთ 200 ₾ (საუკეთესო ფასი)',
        'features': [
            'სრული 1-წლიანი შეუზღუდავი წვდომა',
            'არჩეული კურსის ყველა გაკვეთილი და განახლება',
            'დაზოგეთ 200 ლარი ყოველთვიურ გადახდასთან შედარებით',
            'პრიორიტეტული მხარდაჭერა',
        ],
    },
}

def pricing_view(request):
    course_id = request.GET.get('course_id')
    selected_course = None
    course_access = None
    if course_id:
        selected_course = Course.objects.filter(pk=course_id).first()

    if not selected_course and request.user.is_authenticated and getattr(request.user, 'grade', None):
        selected_course = Course.objects.filter(grade=request.user.grade).first()

    if not selected_course:
        selected_course = Course.objects.first()

    if request.user.is_authenticated and selected_course:
        course_access = UserCourseAccess.objects.filter(user=request.user, course=selected_course).first()

    context = {
        'plans': PLANS_CONFIG,
        'selected_course': selected_course,
        'course_access': course_access,
        'now': timezone.now(),
    }
    return render(request, 'payments/pricing.html', context)


@login_required
@require_POST
def checkout_init_view(request, plan_type):
    if plan_type not in PLANS_CONFIG:
        messages.error(request, "არჩეული სატარიფო პაკეტი არასწორია.")
        return redirect('payments:pricing')

    course_id = request.POST.get('course_id')
    selected_course = None
    if course_id:
        selected_course = Course.objects.filter(pk=course_id).first()
    if not selected_course and getattr(request.user, 'grade', None):
        selected_course = Course.objects.filter(grade=request.user.grade).first()

    if not selected_course:
        messages.error(request, "გთხოვთ აირჩიოთ კურსი კატალოგიდან.")
        return redirect('payments:pricing')

    plan_info = PLANS_CONFIG[plan_type]
    prefix = f"MM_C{selected_course.id}_SUB" if plan_info['is_subscription'] else f"MM_C{selected_course.id}_YEAR"
    order_desc = f"{selected_course.title} - {plan_info['description']}"

    order_id = PaymentOrder.generate_order_id(prefix=prefix)

    # 1. Create initial DB order
    order = PaymentOrder.objects.create(
        order_id=order_id,
        user=request.user,
        course=selected_course,
        plan_type=plan_type,
        amount_gel=plan_info['price_gel'],
        amount_tetri=plan_info['price_tetri'],
        currency='GEL',
        order_desc=order_desc,
        is_subscription=plan_info['is_subscription'],
        status=OrderStatus.CREATED,
    )

    # 2. Build Callback & Response URLs
    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    if site_url:
        server_callback_url = f"{site_url}{reverse('payments:flitt_callback')}"
        response_url = f"{site_url}{reverse('payments:payment_response')}?order_id={order.order_id}"
    else:
        server_callback_url = request.build_absolute_uri(reverse('payments:flitt_callback'))
        response_url = request.build_absolute_uri(reverse('payments:payment_response')) + f'?order_id={order.order_id}'

    # 3. Call Flitt API
    client = FlittPaymentClient()
    flitt_res = client.create_checkout_session(
        order_id=order.order_id,
        amount_tetri=order.amount_tetri,
        order_desc=order.order_desc,
        server_callback_url=server_callback_url,
        response_url=response_url,
        currency=order.currency,
        is_subscription=order.is_subscription,
        sender_email=request.user.email or None,
    )

    response_status = flitt_res.get('response_status', '')
    checkout_url = flitt_res.get('checkout_url', '')
    payment_token = flitt_res.get('payment_token', '')

    order.response_status = response_status
    order.raw_response = flitt_res

    if response_status == 'success' and (checkout_url or payment_token):
        if not checkout_url and payment_token:
            checkout_url = f"https://pay.flitt.com/checkout/{payment_token}"
        order.checkout_url = checkout_url
        order.payment_token = payment_token
        order.status = OrderStatus.PROCESSING
        order.save(update_fields=['checkout_url', 'payment_token', 'status', 'response_status', 'raw_response'])
        return redirect(order.checkout_url)
    else:
        err_msg = flitt_res.get('error_message', 'გადახდის ინიციალიზაცია ვერ მოხერხდა.')
        err_code = flitt_res.get('error_code', '')
        order.status = OrderStatus.DECLINED
        order.response_code = err_code
        order.response_description = err_msg
        order.save(update_fields=['status', 'response_code', 'response_description', 'raw_response'])
        messages.error(request, f"გადახდის სისტემასთან დაკავშირება ვერ მოხერხდა: {err_msg}")
        return redirect('payments:pricing')


@login_required
def checkout_pay_view(request, order_id):
    """
    Direct redirect fallback to Flitt hosted payment page.
    """
    order = get_object_or_404(PaymentOrder, order_id=order_id, user=request.user)
    if order.checkout_url:
        return redirect(order.checkout_url)
    messages.error(request, "გადახდის ბმული ვერ მოიძებნა.")
    return redirect('payments:pricing')



@csrf_exempt
@transaction.atomic
def flitt_callback_view(request):
    """
    Server-to-Server Webhook / Callback from Flitt.
    Fulfills orders and grants user access upon approval.
    """
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed", status=405)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        elif request.body:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except Exception:
                data = request.POST.dict()
        else:
            data = request.POST.dict()
    except Exception as e:
        logger.error("Failed to parse Flitt callback payload: %s", e)
        return HttpResponse("Bad Request", status=400)

    # Flatten nested 'response' wrapper if present
    if 'response' in data and isinstance(data['response'], dict):
        data = data['response']

    # 1. Verify Signature
    if not verify_flitt_signature(data):
        logger.warning("Flitt callback received with INVALID signature. Data: %s", data)
        return HttpResponse("Invalid Signature", status=400)

    order_id = data.get('order_id')
    parent_order_id = data.get('parent_order_id')
    if not order_id and not parent_order_id:
        logger.error("Flitt callback missing order_id.")
        return HttpResponse("Missing order_id", status=400)

    order = None
    if order_id:
        order = PaymentOrder.objects.select_for_update().filter(order_id=order_id).first()

    # Recurring renewal callback support (Flitt calendar charge for subsequent months)
    # Protected against concurrent duplicate webhooks via parent row locking and IntegrityError safety
    if not order and parent_order_id:
        parent_order = (
            PaymentOrder.objects.select_for_update()
            .filter(order_id=parent_order_id)
            .first()
        )
        if parent_order:
            try:
                amount_tetri = int(data.get('amount') or parent_order.amount_tetri)
            except (ValueError, TypeError):
                amount_tetri = parent_order.amount_tetri

            order = (
                PaymentOrder.objects.select_for_update()
                .filter(order_id=order_id)
                .first()
            )
            if not order:
                try:
                    order = PaymentOrder.objects.create(
                        order_id=order_id,
                        user=parent_order.user,
                        course=parent_order.course,
                        plan_type=parent_order.plan_type,
                        amount_gel=Decimal(str(amount_tetri / 100)),
                        amount_tetri=amount_tetri,
                        currency=data.get('currency') or parent_order.currency,
                        order_desc=f"ავტომატური განახლება - {parent_order.order_desc}",
                        is_subscription=True,
                        status=OrderStatus.PROCESSING,
                    )
                except IntegrityError:
                    order = PaymentOrder.objects.select_for_update().get(order_id=order_id)

    if not order:
        logger.error("PaymentOrder %s (parent: %s) not found for Flitt callback.", order_id, parent_order_id)
        return HttpResponse("Order not found", status=404)

    # 2. AMOUNT & CURRENCY INTEGRITY CHECK
    callback_amount = data.get('amount')
    callback_currency = data.get('currency')

    if callback_amount is not None:
        try:
            if int(callback_amount) != order.amount_tetri:
                logger.error(
                    "Amount mismatch for order %s: expected %s tetri, got %s",
                    order.order_id, order.amount_tetri, callback_amount
                )
                return HttpResponse("Amount mismatch", status=400)
        except (ValueError, TypeError):
            logger.error("Invalid amount format in callback for order %s: %s", order.order_id, callback_amount)
            return HttpResponse("Invalid amount", status=400)

    if callback_currency and callback_currency.upper() != order.currency.upper():
        logger.error(
            "Currency mismatch for order %s: expected %s, got %s",
            order.order_id, order.currency, callback_currency
        )
        return HttpResponse("Currency mismatch", status=400)

    # 3. Update Order fields
    order_status = (data.get('order_status') or '').lower()
    order.flitt_payment_id = str(data.get('payment_id', '') or order.flitt_payment_id or '')
    order.masked_card = str(data.get('masked_card', '') or order.masked_card or '')
    order.card_type = str(data.get('card_type', '') or order.card_type or '')
    order.response_status = str(data.get('response_status', '') or order.response_status or '')
    order.response_code = str(data.get('response_code', '') or order.response_code or '')
    order.response_description = str(data.get('response_description', '') or order.response_description or '')
    order.raw_response = data

    # 4. STATE REGRESSION GUARD:
    # If order is already APPROVED, ignore any delayed out-of-order 'processing' webhooks
    if order.status == OrderStatus.APPROVED and order_status == 'processing':
        logger.info("Ignoring delayed 'processing' status for already APPROVED order %s", order.order_id)
        return HttpResponse("OK", status=200)

    if order_status == 'approved':
        # IDEMPOTENCY SAFEGUARD:
        # If this order has already been marked APPROVED, acknowledge without re-granting access.
        if order.status == OrderStatus.APPROVED:
            logger.info("Order %s was already approved. Acknowledging callback without re-granting access.", order.order_id)
            order.save()
            return HttpResponse("OK", status=200)

        order.status = OrderStatus.APPROVED
        order.save()
        rectoken = data.get('rectoken', '')
        course = order.course

        if not course:
            logger.error("Order %s approved by Flitt, but has no associated course! Refusing to assign random course.", order.order_id)
        else:
            UserCourseAccess.grant_or_renew_access(
                user=order.user,
                course=course,
                plan_type=order.plan_type,
                payment_order=order,
                rectoken=rectoken,
            )
            logger.info("Order %s approved! Granted %s access for course '%s' to user %s", order.order_id, order.plan_type, course.title, order.user)
    elif order_status in ('declined', 'expired', 'reversed', 'processing'):
        order.status = order_status
        order.save()
    else:
        order.save()

    # Flitt requires HTTP 200 OK
    return HttpResponse("OK", status=200)


@csrf_exempt
def payment_response_view(request):
    """
    Passive user browser redirect handler after completing checkout on Flitt gateway.
    Strictly read-only display. Fulfillment is exclusively handled by the verified flitt_callback_view webhook.
    """
    order_id = request.GET.get('order_id') or request.POST.get('order_id')
    if not order_id and request.body:
        try:
            body_data = json.loads(request.body.decode('utf-8'))
            if isinstance(body_data, dict):
                if 'response' in body_data and isinstance(body_data['response'], dict):
                    order_id = body_data['response'].get('order_id')
                else:
                    order_id = body_data.get('order_id')
        except Exception:
            pass

    order = None
    if order_id:
        order = PaymentOrder.objects.filter(order_id=order_id).first()

    context = {
        'order': order,
    }
    return render(request, 'payments/payment_status.html', context)


@login_required
@require_POST
def cancel_subscription_view(request):
    """
    Allows an authenticated student to cancel their auto-renewing subscription via Flitt API.
    Stops future billing while preserving access until expires_at.
    """
    now = timezone.now()
    course_id = request.POST.get('course_id')
    active_access = None
    if course_id:
        active_access = UserCourseAccess.objects.filter(
            user=request.user,
            course_id=course_id,
            is_active=True,
            auto_renew=True,
            expires_at__gt=now
        ).first()

    if not active_access:
        active_access = UserCourseAccess.objects.filter(
            user=request.user,
            is_active=True,
            auto_renew=True,
            expires_at__gt=now
        ).first()

    next_url = request.POST.get('next') or request.GET.get('next')
    if not active_access:
        messages.warning(request, "აქტიური ავტომატური გამოწერა ვერ მოიძებნა.")
        if next_url:
            return redirect(next_url)
        return redirect('payments:pricing')

    order = active_access.last_order
    cancel_success = False

    if order:
        client = FlittPaymentClient()
        res = client.cancel_subscription(order.order_id)
        logger.info("Subscription cancellation for order %s result: %s", order.order_id, res)
        if isinstance(res, dict) and (
            res.get('response_status') == 'success' or
            res.get('status') in ('disabled', 'canceled')
        ):
            cancel_success = True
        else:
            logger.error("Flitt returned failure when canceling order %s: %s", order.order_id, res)
            cancel_success = False
    else:
        cancel_success = True

    if cancel_success:
        active_access.auto_renew = False
        active_access.save(update_fields=['auto_renew', 'updated_at'])
        messages.success(
            request,
            f"თქვენი გამოწერა წარმატებით გაუქმდა. არსებული წვდომა ძალაში რჩება {active_access.expires_at.strftime('%Y-%m-%d')}-მდე, რის შემდეგაც თანხა აღარ ჩამოგეჭრებათ."
        )
    else:
        messages.error(
            request,
            "გამოწერის ავტომატური გაუქმება საგადახდო სისტემაში ვერ მოხერხდა. გთხოვთ სცადოთ თავიდან ან მიმართოთ ადმინისტრაციას."
        )

    if next_url:
        return redirect(next_url)
    return redirect('payments:pricing')


