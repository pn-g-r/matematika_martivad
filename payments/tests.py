from unittest.mock import patch
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import PaymentOrder, UserSubscriptionAccess, PlanType, OrderStatus
from .flitt_service import generate_flitt_signature, verify_flitt_signature, FlittPaymentClient

User = get_user_model()

class FlittSignatureTests(TestCase):
    def setUp(self):
        self.secret_key = 'test'

    def test_signature_generation_and_verification(self):
        params = {
            'merchant_id': 1549901,
            'order_id': 'TestOrder123',
            'amount': 5000,
            'currency': 'GEL',
            'order_desc': 'Test Monthly Subscription',
            'server_callback_url': 'http://localhost/payments/callback/',
            'response_url': 'http://localhost/payments/response/',
        }
        signature = generate_flitt_signature(params, secret_key=self.secret_key)
        self.assertTrue(isinstance(signature, str))
        self.assertEqual(len(signature), 40)

        params_with_sig = params.copy()
        params_with_sig['signature'] = signature
        self.assertTrue(verify_flitt_signature(params_with_sig, secret_key=self.secret_key))

        params_tampered = params_with_sig.copy()
        params_tampered['amount'] = 1000
        self.assertFalse(verify_flitt_signature(params_tampered, secret_key=self.secret_key))

    def test_signature_excludes_empty_and_signature_keys(self):
        params = {
            'merchant_id': 1549901,
            'order_id': 'TestOrder123',
            'amount': 40000,
            'currency': 'GEL',
            'empty_field': '',
            'none_field': None,
            'signature': 'previous_sig_to_ignore',
            'response_signature_string': 'ignored_string',
        }
        sig1 = generate_flitt_signature(params, secret_key=self.secret_key)

        clean_params = {
            'merchant_id': 1549901,
            'order_id': 'TestOrder123',
            'amount': 40000,
            'currency': 'GEL',
        }
        sig2 = generate_flitt_signature(clean_params, secret_key=self.secret_key)
        self.assertEqual(sig1, sig2)


class PaymentsWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='555111222',
            phone_number='555111222',
            password='Password123!@#',
            student_name='დავით მაისურაძე',
            parent_name='ნინო მაისურაძე',
            grade='VI',
            book_author='გოგიშვილი',
        )

    def test_pricing_page_renders_successfully(self):
        response = self.client.get(reverse('payments:pricing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '50')
        self.assertContains(response, '400')
        self.assertContains(response, 'ყოველთვიური გამოწერა')
        self.assertContains(response, '1-წლიანი სრული პაკეტი')

    def test_checkout_init_requires_login(self):
        response = self.client.get(reverse('payments:checkout_init', kwargs={'plan_type': 'monthly'}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/accounts/login/' in response.url)

    @patch.object(FlittPaymentClient, 'create_checkout_session')
    def test_checkout_init_monthly_subscription(self, mock_flitt):
        mock_flitt.return_value = {
            'response_status': 'success',
            'checkout_url': 'https://pay.flitt.com/checkout/mock_token_123',
            'payment_token': 'mock_token_123',
        }
        self.client.force_login(self.user)
        response = self.client.get(reverse('payments:checkout_init', kwargs={'plan_type': 'monthly'}))
        
        order = PaymentOrder.objects.filter(user=self.user, plan_type=PlanType.MONTHLY).first()
        self.assertIsNotNone(order)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('payments:checkout_pay', kwargs={'order_id': order.order_id}))

        self.assertEqual(order.amount_gel, Decimal('50.00'))
        self.assertEqual(order.amount_tetri, 5000)
        self.assertTrue(order.is_subscription)
        self.assertEqual(order.status, OrderStatus.PROCESSING)
        self.assertEqual(order.payment_token, 'mock_token_123')

        # Test embedded pay page
        pay_res = self.client.get(reverse('payments:checkout_pay', kwargs={'order_id': order.order_id}))
        self.assertEqual(pay_res.status_code, 200)
        self.assertContains(pay_res, 'flitt-checkout-frame')
        self.assertContains(pay_res, 'https://pay.flitt.com/checkout/mock_token_123')

    @patch.object(FlittPaymentClient, 'create_checkout_session')
    def test_checkout_init_yearly_onetime(self, mock_flitt):
        mock_flitt.return_value = {
            'response_status': 'success',
            'checkout_url': 'https://pay.flitt.com/checkout/mock_token_year_456',
            'payment_token': 'mock_token_year_456',
        }
        self.client.force_login(self.user)
        response = self.client.get(reverse('payments:checkout_init', kwargs={'plan_type': 'yearly'}))
        
        order = PaymentOrder.objects.filter(user=self.user, plan_type=PlanType.YEARLY).first()
        self.assertIsNotNone(order)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('payments:checkout_pay', kwargs={'order_id': order.order_id}))

        self.assertEqual(order.amount_gel, Decimal('400.00'))
        self.assertEqual(order.amount_tetri, 40000)
        self.assertFalse(order.is_subscription)
        self.assertEqual(order.status, OrderStatus.PROCESSING)
        self.assertEqual(order.payment_token, 'mock_token_year_456')

    def test_callback_with_invalid_signature_rejected(self):
        payload = {
            'order_id': 'MM_TEST_999',
            'order_status': 'approved',
            'amount': '5000',
            'signature': 'invalid_signature_value',
        }
        response = self.client.post(
            reverse('payments:flitt_callback'),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_callback_approved_grants_monthly_access(self):
        order = PaymentOrder.objects.create(
            order_id='MM_SUB_123456',
            user=self.user,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            is_subscription=True,
            status=OrderStatus.PROCESSING,
        )

        callback_params = {
            'order_id': order.order_id,
            'merchant_id': 1549901,
            'amount': '5000',
            'currency': 'GEL',
            'order_status': 'approved',
            'response_status': 'success',
            'payment_id': 888777666,
            'masked_card': '444455XXXXXX1111',
            'card_type': 'VISA',
            'rectoken': 'REC_TOKEN_XYZ_999',
        }
        sig = generate_flitt_signature(callback_params, secret_key='test')
        callback_params['signature'] = sig

        response = self.client.post(
            reverse('payments:flitt_callback'),
            data=callback_params,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.APPROVED)
        self.assertEqual(order.flitt_payment_id, '888777666')
        self.assertEqual(order.masked_card, '444455XXXXXX1111')

        access = UserSubscriptionAccess.objects.get(user=self.user)
        self.assertTrue(access.is_active)
        self.assertTrue(access.is_valid_now())
        self.assertEqual(access.plan_type, PlanType.MONTHLY)
        self.assertEqual(access.rectoken, 'REC_TOKEN_XYZ_999')
        self.assertTrue(access.expires_at > timezone.now() + timedelta(days=28))

    def test_callback_approved_grants_yearly_access(self):
        order = PaymentOrder.objects.create(
            order_id='MM_YEAR_987654',
            user=self.user,
            plan_type=PlanType.YEARLY,
            amount_gel=Decimal('400.00'),
            amount_tetri=40000,
            currency='GEL',
            is_subscription=False,
            status=OrderStatus.PROCESSING,
        )

        callback_params = {
            'order_id': order.order_id,
            'merchant_id': 1549901,
            'amount': '40000',
            'currency': 'GEL',
            'order_status': 'approved',
            'response_status': 'success',
            'payment_id': 999111222,
            'masked_card': '555566XXXXXX1111',
            'card_type': 'MASTERCARD',
        }
        sig = generate_flitt_signature(callback_params, secret_key='test')
        callback_params['signature'] = sig

        response = self.client.post(
            reverse('payments:flitt_callback'),
            data=callback_params,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.APPROVED)

        access = UserSubscriptionAccess.objects.get(user=self.user)
        self.assertTrue(access.is_valid_now())
        self.assertEqual(access.plan_type, PlanType.YEARLY)
        self.assertTrue(access.expires_at > timezone.now() + timedelta(days=360))

    def test_payment_response_page(self):
        order = PaymentOrder.objects.create(
            order_id='MM_STATUS_CHECK_001',
            user=self.user,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            status=OrderStatus.APPROVED,
        )
        response = self.client.get(reverse('payments:payment_response') + f'?order_id={order.order_id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'გადახდა წარმატებულია')
        self.assertContains(response, order.order_id)

