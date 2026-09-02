import json
import logging
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .models import PaymentOrder, UserSubscriptionAccess, PlanType, OrderStatus
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
            'სრული წვდომა ყველა კლასის მასალაზე (IV - IX)',
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
            'ყველა კლასი (IV - IX) და მომავალი განახლებები',
            'დაზოგეთ 200 ლარი ყოველთვიურ გადახდასთან შედარებით',
            'პრიორიტეტული მხარდაჭერა',
        ],
    },
}

def pricing_view(request):
    user_access = None
    if request.user.is_authenticated:
        try:
            user_access = request.user.subscription_access
        except UserSubscriptionAccess.DoesNotExist:
            user_access = None

    context = {
        'plans': PLANS_CONFIG,
        'user_access': user_access,
        'now': timezone.now(),
    }
    return render(request, 'payments/pricing.html', context)


@login_required
def checkout_init_view(request, plan_type):
    if plan_type not in PLANS_CONFIG:
        messages.error(request, "არჩეული სატარიფო პაკეტი არასწორია.")
        return redirect('payments:pricing')

    plan_info = PLANS_CONFIG[plan_type]
    prefix = "MM_SUB" if plan_info['is_subscription'] else "MM_YEAR"
    order_id = PaymentOrder.generate_order_id(prefix=prefix)

    # 1. Create initial DB order
    order = PaymentOrder.objects.create(
        order_id=order_id,
        user=request.user,
        plan_type=plan_type,
        amount_gel=plan_info['price_gel'],
        amount_tetri=plan_info['price_tetri'],
        currency='GEL',
        order_desc=plan_info['description'],
        is_subscription=plan_info['is_subscription'],
        status=OrderStatus.CREATED,
    )

    # 2. Build Callback & Response URLs
    server_callback_url = request.build_absolute_uri(reverse('payments:flitt_callback'))
    response_url = request.build_absolute_uri(reverse('payments:payment_response'))

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

    order.response_status = response_status
    order.raw_response = flitt_res

    if response_status == 'success' and checkout_url:
        order.checkout_url = checkout_url
        order.status = OrderStatus.PROCESSING
        order.save(update_fields=['checkout_url', 'status', 'response_status', 'raw_response'])
        return redirect(checkout_url)
    else:
        err_msg = flitt_res.get('error_message', 'გადახდის ინიციალიზაცია ვერ მოხერხდა.')
        err_code = flitt_res.get('error_code', '')
        order.status = OrderStatus.DECLINED
        order.response_code = err_code
        order.response_description = err_msg
        order.save(update_fields=['status', 'response_code', 'response_description', 'raw_response'])
        messages.error(request, f"გადახდის სისტემასთან დაკავშირება ვერ მოხერხდა: {err_msg}")
        return redirect('payments:pricing')


@csrf_exempt
def flitt_callback_view(request):
    """
    Server-to-Server Webhook / Callback from Flitt.
    Fulfills orders and grants user access upon approval.
    """
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed", status=405)

    try:
        if request.content_type == 'application/json' or request.body:
            data = json.loads(request.body.decode('utf-8'))
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
    if not order_id:
        logger.error("Flitt callback missing order_id.")
        return HttpResponse("Missing order_id", status=400)

    try:
        order = PaymentOrder.objects.get(order_id=order_id)
    except PaymentOrder.DoesNotExist:
        logger.error("PaymentOrder %s not found for Flitt callback.", order_id)
        return HttpResponse("Order not found", status=404)

    # 2. Update Order fields
    order_status = data.get('order_status', '').lower()
    order.flitt_payment_id = str(data.get('payment_id', '') or '')
    order.masked_card = str(data.get('masked_card', '') or '')
    order.card_type = str(data.get('card_type', '') or '')
    order.response_status = str(data.get('response_status', '') or '')
    order.response_code = str(data.get('response_code', '') or '')
    order.response_description = str(data.get('response_description', '') or '')
    order.raw_response = data

    if order_status == 'approved':
        order.status = OrderStatus.APPROVED
        order.save()
        # Grant or renew subscription access for user
        rectoken = data.get('rectoken', '')
        UserSubscriptionAccess.grant_or_renew_access(
            user=order.user,
            plan_type=order.plan_type,
            payment_order=order,
            rectoken=rectoken,
        )
        logger.info("Order %s approved! Granted %s access to user %s", order.order_id, order.plan_type, order.user)
    elif order_status in ('declined', 'expired', 'reversed', 'processing'):
        order.status = order_status
        order.save()
    else:
        order.save()

    # Flitt requires HTTP 200 OK
    return HttpResponse("OK", status=200)


def payment_response_view(request):
    """
    User browser redirect handler after completing or canceling checkout in Flitt.
    """
    order_id = request.GET.get('order_id') or request.POST.get('order_id')
    order = None
    if order_id:
        order = PaymentOrder.objects.filter(order_id=order_id).first()

    context = {
        'order': order,
    }
    return render(request, 'payments/payment_status.html', context)

