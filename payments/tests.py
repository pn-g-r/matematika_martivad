import base64
import hashlib
import json
import os
import requests
from urllib.parse import urlparse
from unittest import skipUnless
from unittest.mock import patch
from decimal import Decimal
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta, timezone as datetime_timezone
from .models import (
    CheckoutReservation,
    FulfilledPayment,
    PaymentOrder,
    UserCourseAccess,
    PlanType,
    OrderStatus,
    add_calendar_months,
)
from courses.models import Course, Chapter, Lesson
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


class FlittCheckoutConfigTests(TestCase):
    @patch('payments.flitt_service.Checkout')
    @patch('payments.flitt_service.Api')
    def test_subscription_checkout_mandatory_schedule_and_georgian(self, _mock_api, mock_checkout_cls):
        mock_checkout = mock_checkout_cls.return_value
        mock_checkout.subscription.return_value = {
            'checkout_url': 'https://pay.flitt.com/checkout/sub_token',
            'payment_id': '123',
        }

        client = FlittPaymentClient()
        result = client.create_checkout_session(
            order_id='MM_TEST_SUB',
            amount_tetri=5000,
            order_desc='Test subscription',
            server_callback_url='http://example.com/callback/',
            response_url='http://example.com/response/',
            is_subscription=True,
        )

        self.assertEqual(result['response_status'], 'success')
        sub_data = mock_checkout.subscription.call_args[0][0]
        self.assertEqual(sub_data['lang'], 'ka')
        self.assertEqual(sub_data['recurring_data']['state'], 'shown_readonly')
        self.assertEqual(sub_data['recurring_data']['quantity'], 12)
        self.assertRegex(sub_data['recurring_data']['start_time'], r'^\d{4}-\d{2}-\d{2}$')
        self.assertEqual(_mock_api.call_args.kwargs['timeout'], 5)

    @patch('payments.flitt_service.Checkout.response', return_value={'checkout_url': 'https://pay.flitt.com/checkout/test'})
    @patch('payments.flitt_service.Api.post', return_value={})
    def test_subscription_passes_real_sdk_validation_without_network(self, mock_post, _mock_response):
        result = FlittPaymentClient(merchant_id=1549901, secret_key='test').create_checkout_session(
            order_id='MM_TEST_SUB_SDK',
            amount_tetri=5000,
            order_desc='Test subscription',
            server_callback_url='https://example.com/callback/',
            response_url='https://example.com/response/',
            is_subscription=True,
        )
        self.assertEqual(result['response_status'], 'success')
        mock_post.assert_called_once()

    @patch('payments.flitt_service.Api.post', side_effect=requests.exceptions.Timeout)
    def test_checkout_timeout_returns_unknown_result(self, _mock_post):
        result = FlittPaymentClient(merchant_id=1549901, secret_key='test').create_checkout_session(
            order_id='MM_TIMEOUT_SUB', amount_tetri=5000, order_desc='Test',
            server_callback_url='https://example.com/callback/',
            response_url='https://example.com/response/', is_subscription=True,
        )
        self.assertEqual(result['response_status'], 'failure')
        self.assertEqual(result['error_code'], 'TIMEOUT')
        self.assertNotIn('checkout_url', result)

    @patch('payments.flitt_service.Checkout')
    @patch('payments.flitt_service.Api')
    def test_onetime_checkout_uses_georgian(self, _mock_api, mock_checkout_cls):
        mock_checkout = mock_checkout_cls.return_value
        mock_checkout.url.return_value = {
            'response_status': 'success',
            'checkout_url': 'https://pay.flitt.com/checkout/year_token',
            'payment_id': '456',
        }

        client = FlittPaymentClient()
        result = client.create_checkout_session(
            order_id='MM_TEST_YEAR',
            amount_tetri=40000,
            order_desc='Test yearly',
            server_callback_url='http://example.com/callback/',
            response_url='http://example.com/response/',
            is_subscription=False,
        )

        self.assertEqual(result['response_status'], 'success')
        order_data = mock_checkout.url.call_args[0][0]
        self.assertEqual(order_data['lang'], 'ka')
        self.assertEqual(_mock_api.call_args.kwargs['timeout'], 5)


class PaymentsWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.course = Course.objects.create(
            title='VI კლასის მათემატიკა',
            grade='VI',
            short_description='Short',
            long_description='Long',
            instructor_name='გიორგი',
            duration='30 სთ',
            lessons_count=10,
            video_url='https://youtube.com/embed/test',
            price=Decimal('50.00'),
        )
        self.user = User.objects.create_user(
            username='555111222',
            phone_number='555111222',
            password='Password123!@#',
            student_name='დავით მაისურაძე',
            parent_name='ნინო მაისურაძე',
            grade='VI',
            book_author='გოგიშვილი',
        )

    @skipUnless(os.environ.get('RUN_FLITT_SANDBOX') == '1', 'Explicit sandbox opt-in required')
    @override_settings(SITE_URL='https://example.invalid')
    def test_live_sandbox_checkout_and_admin_status_query(self):
        self.assertEqual(settings.FLITT_MERCHANT_ID, 1549901)
        self.assertEqual(settings.FLITT_SECRET_KEY, 'test')
        self.client.force_login(self.user)
        for plan in (PlanType.MONTHLY, PlanType.YEARLY):
            with self.subTest(plan=plan):
                response = self.client.post(
                    reverse('payments:checkout_init', kwargs={'plan_type': plan}),
                    data={'course_id': self.course.id},
                )
                order = PaymentOrder.objects.get(user=self.user, course=self.course, plan_type=plan)
                self.assertEqual(response.status_code, 302, order.response_description)
                self.assertEqual(order.status, OrderStatus.PROCESSING, order.response_description)
                self.assertEqual(urlparse(response.url).hostname, 'pay.flitt.com', order.response_description)
                status_info = FlittPaymentClient().get_order_status(order.order_id)
                self.assertEqual(status_info.get('order_id'), order.order_id)
                self.assertIn(status_info.get('order_status'), ('created', 'processing'))
                with patch.object(admin.site._registry[PaymentOrder], 'message_user'):
                    admin.site._registry[PaymentOrder].sync_with_flitt_action(
                        None, PaymentOrder.objects.filter(pk=order.pk)
                    )
                order.refresh_from_db()
                self.assertNotEqual(order.status, OrderStatus.APPROVED)
                self.assertFalse(UserCourseAccess.objects.filter(user=self.user, course=self.course).exists())

    def test_pricing_page_renders_successfully(self):
        response = self.client.get(reverse('payments:pricing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '50')
        self.assertContains(response, '400')
        self.assertContains(response, 'ყოველთვიური გამოწერა')
        self.assertContains(response, '1-წლიანი სრული პაკეტი')

    def test_pricing_without_course_requires_catalog_selection(self):
        user_no_grade = User.objects.create_user(
            username='555999888',
            phone_number='555999888',
            password='Password123!@#',
            student_name='ანა ბერიძე',
            parent_name='მარიამ ბერიძე',
            grade='',
            book_author='გოგიშვილი',
        )
        self.client.force_login(user_no_grade)
        response = self.client.get(reverse('payments:pricing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'კატალოგში გადასვლა')
        self.assertContains(response, 'ჯერ აირჩიეთ კურსი კატალოგიდან')
        self.assertNotContains(response, 'name="course_id"')

    def test_callback_accepts_amount_stored_on_order(self):
        order = PaymentOrder.objects.create(
            order_id='MM_LEGACY_PRICE_001',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('45.00'),
            amount_tetri=4500,
            currency='GEL',
            is_subscription=True,
            status=OrderStatus.PROCESSING,
        )
        callback_params = {
            'order_id': order.order_id,
            'merchant_id': 1549901,
            'amount': '4500',
            'currency': 'GEL',
            'order_status': 'approved',
            'response_status': 'success',
            'payment_id': 777888999,
        }
        callback_params['signature'] = generate_flitt_signature(callback_params, secret_key='test')
        response = self.client.post(
            reverse('payments:flitt_callback'),
            data=callback_params,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.APPROVED)

    @patch.object(FlittPaymentClient, 'create_checkout_session')
    def test_checkout_timeout_keeps_order_outcome_unknown(self, mock_flitt):
        mock_flitt.return_value = {
            'response_status': 'failure', 'error_code': 'TIMEOUT',
            'error_message': 'Flitt did not respond in time.',
        }
        self.client.force_login(self.user)
        result = self.client.post(
            reverse('payments:checkout_init', kwargs={'plan_type': 'monthly'}),
            data={'course_id': self.course.pk},
        )
        self.assertEqual(result.status_code, 302)
        order = PaymentOrder.objects.get(user=self.user, course=self.course)
        self.assertEqual(order.status, OrderStatus.PROCESSING)
        self.assertEqual(order.response_code, 'TIMEOUT')
        self.assertFalse(order.checkout_url)
        self.assertFalse(UserCourseAccess.objects.filter(user=self.user, course=self.course).exists())
        self.assertTrue(CheckoutReservation.objects.filter(user=self.user, course=self.course).exists())

    @patch.object(FlittPaymentClient, 'create_checkout_session')
    def test_repeated_checkout_reuses_existing_session(self, mock_flitt):
        mock_flitt.return_value = {
            'response_status': 'success',
            'checkout_url': 'https://pay.flitt.com/checkout/one-session',
            'payment_token': 'one-session',
        }
        self.client.force_login(self.user)
        checkout_url = reverse('payments:checkout_init', kwargs={'plan_type': 'monthly'})
        first = self.client.post(checkout_url, data={'course_id': self.course.pk})
        second = self.client.post(checkout_url, data={'course_id': self.course.pk})
        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(first.url, second.url)
        self.assertEqual(mock_flitt.call_count, 1)
        self.assertEqual(PaymentOrder.objects.filter(user=self.user, course=self.course).count(), 1)
        self.assertEqual(CheckoutReservation.objects.filter(user=self.user, course=self.course).count(), 1)

    def test_checkout_init_requires_login(self):
        response = self.client.post(reverse('payments:checkout_init', kwargs={'plan_type': 'monthly'}), data={'course_id': self.course.id})
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/accounts/login/' in response.url)

    def test_checkout_init_rejects_get_request(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('payments:checkout_init', kwargs={'plan_type': 'monthly'}))
        self.assertEqual(response.status_code, 405)

    @patch.object(FlittPaymentClient, 'create_checkout_session')
    def test_checkout_init_monthly_subscription(self, mock_flitt):
        mock_flitt.return_value = {
            'response_status': 'success',
            'checkout_url': 'https://pay.flitt.com/checkout/mock_token_123',
            'payment_token': 'mock_token_123',
        }
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('payments:checkout_init', kwargs={'plan_type': 'monthly'}),
            data={'course_id': self.course.id}
        )
        
        order = PaymentOrder.objects.filter(user=self.user, plan_type=PlanType.MONTHLY).first()
        self.assertIsNotNone(order)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://pay.flitt.com/checkout/mock_token_123')

        self.assertEqual(order.amount_gel, Decimal('50.00'))
        self.assertEqual(order.amount_tetri, 5000)
        self.assertTrue(order.is_subscription)
        self.assertEqual(order.status, OrderStatus.PROCESSING)
        self.assertEqual(order.payment_token, 'mock_token_123')

        # Test direct redirect fallback on pay URL
        pay_res = self.client.get(reverse('payments:checkout_pay', kwargs={'order_id': order.order_id}))
        self.assertEqual(pay_res.status_code, 302)
        self.assertEqual(pay_res.url, 'https://pay.flitt.com/checkout/mock_token_123')

    @patch.object(FlittPaymentClient, 'create_checkout_session')
    def test_checkout_init_yearly_onetime(self, mock_flitt):
        mock_flitt.return_value = {
            'response_status': 'success',
            'checkout_url': 'https://pay.flitt.com/checkout/mock_token_year_456',
            'payment_token': 'mock_token_year_456',
        }
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('payments:checkout_init', kwargs={'plan_type': 'yearly'}),
            data={'course_id': self.course.id}
        )
        
        order = PaymentOrder.objects.filter(user=self.user, plan_type=PlanType.YEARLY).first()
        self.assertIsNotNone(order)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://pay.flitt.com/checkout/mock_token_year_456')

        self.assertEqual(order.amount_gel, Decimal('400.00'))
        self.assertEqual(order.amount_tetri, 40000)
        self.assertFalse(order.is_subscription)
        self.assertEqual(order.status, OrderStatus.PROCESSING)
        self.assertEqual(order.payment_token, 'mock_token_year_456')

        # Test direct redirect fallback on pay URL
        pay_res = self.client.get(reverse('payments:checkout_pay', kwargs={'order_id': order.order_id}))
        self.assertEqual(pay_res.status_code, 302)
        self.assertEqual(pay_res.url, 'https://pay.flitt.com/checkout/mock_token_year_456')

    def test_invalid_callback_does_not_open_a_transaction(self):
        payload = {'order_id': 'MM_NO_TRANSACTION', 'signature': 'invalid'}
        with patch('payments.views.transaction.atomic', side_effect=AssertionError('Unexpected transaction')) as atomic:
            result = self.client.post(
                reverse('payments:flitt_callback'), data=payload, content_type='application/json',
            )
        self.assertEqual(result.status_code, 400)
        atomic.assert_not_called()

    def test_renewal_currency_mismatch_creates_no_child_order(self):
        root = PaymentOrder.objects.create(
            order_id='MM_CURRENCY_ROOT', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.APPROVED,
        )
        payload = {
            'order_id': 'MM_WRONG_CURRENCY_CHILD', 'parent_order_id': root.order_id,
            'merchant_id': 1549901, 'amount': '5000', 'currency': 'USD',
            'order_status': 'approved', 'payment_id': 123456,
        }
        payload['signature'] = generate_flitt_signature(payload, secret_key='test')
        result = self.client.post(
            reverse('payments:flitt_callback'), data=payload, content_type='application/json',
        )
        self.assertEqual(result.status_code, 400)
        self.assertFalse(PaymentOrder.objects.filter(order_id=payload['order_id']).exists())

    def test_callback_with_invalid_signature_rejected(self):
        payload = {
            'order_id': 'MM_TEST_999',
            'order_status': 'approved',
            'amount': '5000',
            'signature': 'invalid_signature_value',
        }
        payload['rectoken'] = 'sensitive_recurring_token'
        with self.assertLogs('payments.views', level='WARNING') as captured:
            response = self.client.post(
                reverse('payments:flitt_callback'),
                data=payload,
                content_type='application/json'
            )
        self.assertEqual(response.status_code, 400)
        self.assertNotIn('sensitive_recurring_token', ' '.join(captured.output))

    def test_callback_approved_grants_monthly_access(self):
        order = PaymentOrder.objects.create(
            order_id='MM_SUB_123456',
            user=self.user,
            course=self.course,
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
        self.assertFalse(CheckoutReservation.objects.filter(order=order).exists())
        self.assertEqual(order.flitt_payment_id, '888777666')
        self.assertEqual(order.masked_card, '444455XXXXXX1111')

        access = UserCourseAccess.objects.get(user=self.user, course=self.course)
        self.assertTrue(access.is_active)
        self.assertTrue(access.is_valid_now())
        self.assertEqual(access.plan_type, PlanType.MONTHLY)
        self.assertEqual(access.rectoken, 'REC_TOKEN_XYZ_999')
        self.assertEqual(access.subscription_order_id, order.order_id)
        self.assertTrue(access.expires_at > timezone.now() + timedelta(days=28))

    def test_callback_reversal_revokes_period_once_and_ignores_replayed_approval(self):
        order = PaymentOrder.objects.create(
            order_id='MM_REVERSAL_CALLBACK', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.PROCESSING,
        )
        CheckoutReservation.objects.create(user=self.user, course=self.course, order=order)

        def send_status(status):
            payload = {
                'order_id': order.order_id,
                'merchant_id': 1549901,
                'amount': '5000',
                'currency': 'GEL',
                'order_status': status,
                'payment_id': 'reversal-payment-1',
            }
            payload['signature'] = generate_flitt_signature(payload, secret_key='test')
            return self.client.post(
                reverse('payments:flitt_callback'), data=payload, content_type='application/json',
            )

        self.assertEqual(send_status('approved').status_code, 200)
        access = UserCourseAccess.objects.get(user=self.user, course=self.course)
        original_expiry = access.expires_at
        self.assertFalse(CheckoutReservation.objects.filter(order=order).exists())

        self.assertEqual(send_status('reversed').status_code, 200)
        access.refresh_from_db()
        reversed_expiry = access.expires_at
        self.assertLess(reversed_expiry, original_expiry)
        self.assertFalse(access.is_valid_now())

        self.assertEqual(send_status('reversed').status_code, 200)
        self.assertEqual(send_status('approved').status_code, 200)
        access.refresh_from_db()
        self.assertEqual(access.expires_at, reversed_expiry)
        fulfillment = FulfilledPayment.objects.get(order=order, payment_id='reversal-payment-1')
        self.assertIsNotNone(fulfillment.reversed_at)

    def test_declined_callback_releases_checkout_reservation(self):
        order = PaymentOrder.objects.create(
            order_id='MM_DECLINED_RESERVATION', user=self.user, course=self.course,
            plan_type=PlanType.YEARLY, amount_gel=Decimal('400.00'), amount_tetri=40000,
            currency='GEL', status=OrderStatus.PROCESSING,
        )
        CheckoutReservation.objects.create(user=self.user, course=self.course, order=order)
        payload = {
            'order_id': order.order_id, 'merchant_id': 1549901,
            'amount': '40000', 'currency': 'GEL', 'order_status': 'declined',
        }
        payload['signature'] = generate_flitt_signature(payload, secret_key='test')
        response = self.client.post(
            reverse('payments:flitt_callback'), data=payload, content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CheckoutReservation.objects.filter(order=order).exists())

    def test_callback_approved_grants_yearly_access(self):
        order = PaymentOrder.objects.create(
            order_id='MM_YEAR_987654',
            user=self.user,
            course=self.course,
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

        access = UserCourseAccess.objects.get(user=self.user, course=self.course)
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

    @patch.object(FlittPaymentClient, 'create_checkout_session')
    def test_course_specific_checkout_and_callback_grant(self, mock_flitt):
        mock_flitt.return_value = {
            'response_status': 'success',
            'checkout_url': 'https://pay.flitt.com/checkout/mock_course_token',
            'payment_token': 'mock_course_token',
        }
        course_a = Course.objects.create(
            title='VI კლასის მათემატიკა',
            grade='VI',
            short_description='Short',
            long_description='Long',
            instructor_name='გიორგი',
            duration='30 სთ',
            lessons_count=10,
            video_url='https://youtube.com/embed/test',
            price=Decimal('50.00'),
        )
        course_b = Course.objects.create(
            title='VII კლასის მათემატიკა',
            grade='VII',
            short_description='Short',
            long_description='Long',
            instructor_name='გიორგი',
            duration='30 სთ',
            lessons_count=10,
            video_url='https://youtube.com/embed/test',
            price=Decimal('50.00'),
        )

        self.client.force_login(self.user)
        # 1. Checkout init with course_id
        response = self.client.post(
            reverse('payments:checkout_init', kwargs={'plan_type': 'monthly'}),
            data={'course_id': course_a.id}
        )
        self.assertEqual(response.status_code, 302)
        order = PaymentOrder.objects.filter(user=self.user, course=course_a).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.course, course_a)
        self.assertTrue(order.order_id.startswith(f"MM_C{course_a.id}_SUB"))
        self.assertTrue(course_a.title in order.order_desc)

        # 2. Flitt callback approving order for Course A
        callback_params = {
            'order_id': order.order_id,
            'merchant_id': 1549901,
            'amount': '5000',
            'currency': 'GEL',
            'order_status': 'approved',
            'response_status': 'success',
            'rectoken': 'rec_course_token_xyz',
        }
        sig = generate_flitt_signature(callback_params, secret_key='test')
        callback_params['signature'] = sig

        res = self.client.post(
            reverse('payments:flitt_callback'),
            data=callback_params,
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)

        # 3. Verify user has access to Course A, but NOT Course B
        access_a = UserCourseAccess.objects.filter(user=self.user, course=course_a).first()
        self.assertIsNotNone(access_a)
        self.assertTrue(access_a.is_valid_now())
        self.assertEqual(access_a.rectoken, 'rec_course_token_xyz')

        access_b = UserCourseAccess.objects.filter(user=self.user, course=course_b).first()
        self.assertIsNone(access_b)

    def test_course_detail_paywall_view(self):
        course_a = Course.objects.create(
            title='VI კლასის მათემატიკა',
            grade='VI',
            short_description='Short',
            long_description='Long',
            instructor_name='გიორგი',
            duration='30 სთ',
            lessons_count=10,
            video_url='https://youtube.com/embed/test',
            price=Decimal('50.00'),
        )
        course_b = Course.objects.create(
            title='VII კლასის მათემატიკა',
            grade='VII',
            short_description='Short',
            long_description='Long',
            instructor_name='გიორგი',
            duration='30 სთ',
            lessons_count=10,
            video_url='https://youtube.com/embed/test',
            price=Decimal('50.00'),
        )

        # Unauthenticated user visiting course_a -> has_access=False
        res = self.client.get(reverse('course_detail', kwargs={'pk': course_a.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.context['has_access'])
        self.assertContains(res, 'კურსის დაწყება')

        # Authenticated user without payment visiting course_a -> has_access=False
        self.client.force_login(self.user)
        res = self.client.get(reverse('course_detail', kwargs={'pk': course_a.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.context['has_access'])

        # Grant access to course_a
        UserCourseAccess.grant_or_renew_access(
            user=self.user,
            course=course_a,
            plan_type=PlanType.MONTHLY
        )

        # Visiting course_a -> has_access=True
        res_a = self.client.get(reverse('course_detail', kwargs={'pk': course_a.pk}))
        self.assertTrue(res_a.context['has_access'])
        self.assertNotContains(res_a, 'სწავლის გაგრძელება')
        self.assertContains(res_a, 'სწავლის შეწყვეტა')

        # Visiting course_b -> has_access=False (strictly isolated!)
        res_b = self.client.get(reverse('course_detail', kwargs={'pk': course_b.pk}))
        self.assertFalse(res_b.context['has_access'])
        self.assertContains(res_b, 'კურსის დაწყება')

    def test_paid_student_navigation_elements(self):
        course = Course.objects.create(
            title='VI კლასის მათემატიკა',
            grade='VI',
            short_description='Short',
            long_description='Long',
            instructor_name='გიორგი',
            duration='30 სთ',
            lessons_count=10,
            video_url='https://youtube.com/embed/test',
            price=Decimal('50.00'),
        )

        # 1. Anonymous user: no button, no green line
        res = self.client.get(reverse('home'))
        self.assertNotContains(res, 'ჩემი გაკვეთილები')
        self.assertNotContains(res, 'განაგრძეთ მეცადინეობა')

        # 2. Logged in unpaid student: no button, no green line
        self.client.force_login(self.user)
        res = self.client.get(reverse('home'))
        self.assertNotContains(res, 'ჩემი გაკვეთილები')
        self.assertNotContains(res, 'განაგრძეთ მეცადინეობა')

        # 3. Staff / Admin user: excluded per business requirements
        admin_user = User.objects.create_user(
            username='admin_test',
            phone_number='555999000',
            password='Password123!',
            is_staff=True,
        )
        UserCourseAccess.grant_or_renew_access(user=admin_user, course=course, plan_type=PlanType.MONTHLY)
        self.client.force_login(admin_user)
        res = self.client.get(reverse('home'))
        self.assertNotContains(res, 'ჩემი გაკვეთილები')
        self.assertNotContains(res, 'განაგრძეთ მეცადინეობა')

        # 4. Regular paid student: has 'ჩემი გაკვეთილები' button near logout
        UserCourseAccess.grant_or_renew_access(user=self.user, course=course, plan_type=PlanType.MONTHLY)
        self.client.force_login(self.user)
        res = self.client.get(reverse('home'))
        self.assertContains(res, 'ჩემი გაკვეთილები')
        self.assertNotContains(res, 'განაგრძეთ მეცადინეობა')
        self.assertNotContains(res, 'data-my-lessons-dropdown')
        self.assertContains(res, reverse('course_detail', kwargs={'pk': course.id}))

    def test_paid_student_my_lessons_dropdown_with_two_or_more_courses(self):
        course_a = Course.objects.create(
            title='VI კლასის მათემატიკა',
            grade='VI',
            short_description='Short',
            long_description='Long',
            instructor_name='გიორგი',
            duration='30 სთ',
            lessons_count=10,
            video_url='https://youtube.com/embed/test',
            price=Decimal('50.00'),
            order=1,
        )
        course_b = Course.objects.create(
            title='VII კლასის მათემატიკა',
            grade='VII',
            short_description='Short',
            long_description='Long',
            instructor_name='გიორგი',
            duration='30 სთ',
            lessons_count=10,
            video_url='https://youtube.com/embed/test',
            price=Decimal('50.00'),
            order=2,
        )
        UserCourseAccess.grant_or_renew_access(user=self.user, course=course_a, plan_type=PlanType.MONTHLY)
        UserCourseAccess.grant_or_renew_access(user=self.user, course=course_b, plan_type=PlanType.MONTHLY)
        self.client.force_login(self.user)
        res = self.client.get(reverse('home'))
        self.assertContains(res, 'ჩემი გაკვეთილები')
        self.assertContains(res, 'data-my-lessons-dropdown')
        self.assertContains(res, 'აირჩიეთ კურსი')
        self.assertContains(res, course_a.title)
        self.assertContains(res, course_b.title)

    def test_callback_idempotency_does_not_double_access_duration(self):
        order = PaymentOrder.objects.create(
            order_id='MM_IDEMPOTENT_001',
            user=self.user,
            course=self.course,
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
            'payment_id': 12345678,
            'rectoken': 'rec_token_idem',
        }
        callback_params['signature'] = generate_flitt_signature(callback_params, secret_key='test')

        # 1. First callback delivery: should approve order and grant 30 days
        res1 = self.client.post(reverse('payments:flitt_callback'), data=callback_params, content_type='application/json')
        self.assertEqual(res1.status_code, 200)
        access = UserCourseAccess.objects.get(user=self.user, course=self.course)
        initial_expiry = access.expires_at

        # 2. Duplicate callback delivery: should return 200 OK but NOT extend expiry again
        res2 = self.client.post(reverse('payments:flitt_callback'), data=callback_params, content_type='application/json')
        self.assertEqual(res2.status_code, 200)
        access.refresh_from_db()
        self.assertEqual(access.expires_at, initial_expiry)

    def test_approved_unfulfilled_order_replay_grants_access_once(self):
        for plan in (PlanType.MONTHLY, PlanType.YEARLY):
            with self.subTest(plan=plan):
                order = PaymentOrder.objects.create(
                    order_id=f'MM_UNFULFILLED_{plan}', user=self.user, course=self.course,
                    plan_type=plan, amount_gel=Decimal('50.00'), amount_tetri=5000,
                    currency='GEL', is_subscription=plan == PlanType.MONTHLY,
                    status=OrderStatus.APPROVED,
                )
                payload = {
                    'order_id': order.order_id, 'merchant_id': 1549901,
                    'amount': '5000', 'currency': 'GEL', 'order_status': 'approved',
                    'payment_id': 7001 if plan == PlanType.MONTHLY else 7002,
                }
                payload['signature'] = generate_flitt_signature(payload, secret_key='test')
                url = reverse('payments:flitt_callback')
                self.assertEqual(self.client.post(url, data=payload, content_type='application/json').status_code, 200)
                access = UserCourseAccess.objects.get(user=self.user, course=self.course)
                expiry = access.expires_at
                self.assertEqual(self.client.post(url, data=payload, content_type='application/json').status_code, 200)
                access.refresh_from_db()
                order.refresh_from_db()
                self.assertEqual(access.expires_at, expiry)
                self.assertIsNotNone(order.access_granted_at)
                self.assertEqual(order.fulfilled_payments.count(), 1)
                access.delete()

    def test_approved_unfulfilled_child_replay_preserves_subscription_root(self):
        root = PaymentOrder.objects.create(
            order_id='MM_UNFULFILLED_PARENT', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            is_subscription=True, status=OrderStatus.APPROVED,
        )
        child = PaymentOrder.objects.create(
            order_id='MM_UNFULFILLED_CHILD', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            is_subscription=True, status=OrderStatus.APPROVED,
            subscription_parent_order_id=root.order_id,
        )
        payload = {
            'order_id': child.order_id, 'merchant_id': 1549901,
            'amount': '5000', 'currency': 'GEL', 'order_status': 'approved',
            'payment_id': 7003,
        }
        payload['signature'] = generate_flitt_signature(payload, secret_key='test')
        url = reverse('payments:flitt_callback')
        self.assertEqual(self.client.post(url, data=payload, content_type='application/json').status_code, 200)
        access = UserCourseAccess.objects.get(user=self.user, course=self.course)
        self.assertEqual(access.subscription_order_id, root.order_id)
        expiry = access.expires_at
        self.assertEqual(self.client.post(url, data=payload, content_type='application/json').status_code, 200)
        access.refresh_from_db()
        self.assertEqual(access.expires_at, expiry)
        self.assertEqual(child.fulfilled_payments.count(), 1)

    def test_unknown_signed_callback_status_is_logged_without_grant(self):
        order = PaymentOrder.objects.create(
            order_id='MM_UNKNOWN_STATUS', user=self.user, course=self.course,
            plan_type=PlanType.YEARLY, amount_gel=Decimal('400.00'), amount_tetri=40000,
            status=OrderStatus.PROCESSING,
        )
        payload = {'order_id': order.order_id, 'merchant_id': 1549901,
                   'order_status': 'unexpected', 'payment_id': 7123}
        payload['signature'] = generate_flitt_signature(payload, secret_key='test')
        with self.assertLogs('payments.views', level='WARNING') as captured:
            self.assertEqual(self.client.post(
                reverse('payments:flitt_callback'), data=payload, content_type='application/json',
            ).status_code, 200)
        self.assertIn('unexpected', captured.output[0])
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.PROCESSING)
        self.assertFalse(UserCourseAccess.objects.filter(user=self.user, course=self.course).exists())

    def test_same_order_renewal_grants_once_per_payment_id(self):
        order = PaymentOrder.objects.create(
            order_id='MM_SAME_ORDER_RENEWAL',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            is_subscription=True,
            status=OrderStatus.PROCESSING,
        )

        def deliver(payment_id):
            payload = {
                'order_id': order.order_id,
                'merchant_id': 1549901,
                'amount': '5000',
                'currency': 'GEL',
                'order_status': 'approved',
                'payment_id': payment_id,
            }
            payload['signature'] = generate_flitt_signature(payload, secret_key='test')
            return self.client.post(
                reverse('payments:flitt_callback'), data=payload, content_type='application/json'
            )

        self.assertEqual(deliver(1001).status_code, 200)
        access = UserCourseAccess.objects.get(user=self.user, course=self.course)
        first_expiry = access.expires_at
        self.assertEqual(first_expiry, add_calendar_months(access.starts_at))
        self.assertEqual(deliver(1002).status_code, 200)
        access.refresh_from_db()
        self.assertEqual(access.expires_at, add_calendar_months(access.starts_at, 2))
        self.assertEqual(deliver(1001).status_code, 200)
        self.assertEqual(deliver(1002).status_code, 200)
        access.refresh_from_db()
        self.assertEqual(access.expires_at, add_calendar_months(access.starts_at, 2))

    @patch('payments.flitt_service.requests.post')
    def test_admin_sync_uses_signed_status_and_is_idempotent(self, mock_post):
        order = PaymentOrder.objects.create(
            order_id='MM_ADMIN_STATUS_TEST', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.PROCESSING,
        )
        payload = {
            'order_id': order.order_id, 'merchant_id': 1549901,
            'order_status': 'approved', 'amount': '5000', 'currency': 'GEL',
            'payment_id': 999555,
        }
        payload['signature'] = generate_flitt_signature(payload, secret_key='test')
        mock_post.return_value.json.return_value = {'response': payload}
        action = admin.site._registry[PaymentOrder]
        with patch.object(action, 'message_user'):
            action.sync_with_flitt_action(None, PaymentOrder.objects.filter(pk=order.pk))
            access = UserCourseAccess.objects.get(user=self.user, course=self.course)
            first_expiry = access.expires_at
            action.sync_with_flitt_action(None, PaymentOrder.objects.filter(pk=order.pk))
        order.refresh_from_db()
        access.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.APPROVED)
        self.assertEqual(access.expires_at, first_expiry)
        self.assertEqual(order.fulfilled_payments.count(), 1)

    @patch('payments.flitt_service.requests.post')
    def test_admin_sync_reverses_fulfilled_payment_once(self, mock_post):
        order = PaymentOrder.objects.create(
            order_id='MM_ADMIN_REVERSAL', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.APPROVED,
        )
        order.fulfill_access_if_needed(payment_id='admin-reversal-payment')
        access = UserCourseAccess.objects.get(user=self.user, course=self.course)
        granted_expiry = access.expires_at
        payload = {
            'order_id': order.order_id, 'merchant_id': 1549901,
            'order_status': 'reversed', 'amount': '5000', 'currency': 'GEL',
            'payment_id': 'admin-reversal-payment',
        }
        payload['signature'] = generate_flitt_signature(payload, secret_key='test')
        mock_post.return_value.json.return_value = {'response': payload}
        action = admin.site._registry[PaymentOrder]
        with patch.object(action, 'message_user'):
            action.sync_with_flitt_action(None, PaymentOrder.objects.filter(pk=order.pk))
            access.refresh_from_db()
            reversed_expiry = access.expires_at
            action.sync_with_flitt_action(None, PaymentOrder.objects.filter(pk=order.pk))
        order.refresh_from_db()
        access.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.REVERSED)
        self.assertLess(reversed_expiry, granted_expiry)
        self.assertEqual(access.expires_at, reversed_expiry)
        self.assertTrue(FulfilledPayment.objects.get(order=order).reversed_at)

    @patch('payments.flitt_service.requests.post')
    def test_admin_sync_supports_signed_v2_status(self, mock_post):
        order = PaymentOrder.objects.create(
            order_id='MM_ADMIN_V2_STATUS', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.PROCESSING,
        )
        payload = {
            'order': {
                'order_id': order.order_id, 'merchant_id': 1549901,
                'order_status': 'approved', 'amount': '5000', 'currency': 'GEL',
                'payment_id': 999557,
            }
        }
        encoded = base64.b64encode(json.dumps(payload).encode('utf-8')).decode('ascii')
        envelope = {
            'version': '2.0', 'response_status': 'success', 'data': encoded,
            'signature': hashlib.sha1(f'test|{encoded}'.encode('utf-8')).hexdigest(),
        }
        mock_post.return_value.json.return_value = {'response': envelope}
        action = admin.site._registry[PaymentOrder]
        with patch.object(action, 'message_user'):
            action.sync_with_flitt_action(None, PaymentOrder.objects.filter(pk=order.pk))
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.APPROVED)
        self.assertTrue(UserCourseAccess.objects.get(user=self.user, course=self.course).is_valid_now())

        envelope['signature'] = 'invalid'
        with patch.object(action, 'message_user'):
            action.sync_with_flitt_action(None, PaymentOrder.objects.filter(pk=order.pk))
        self.assertEqual(order.fulfilled_payments.count(), 1)

    @patch('payments.flitt_service.requests.post')
    def test_admin_sync_rejects_invalid_or_mismatched_status(self, mock_post):
        order = PaymentOrder.objects.create(
            order_id='MM_ADMIN_INVALID_STATUS', user=self.user, course=self.course,
            plan_type=PlanType.YEARLY, amount_gel=Decimal('400.00'), amount_tetri=40000,
            currency='GEL', status=OrderStatus.PROCESSING,
        )
        payload = {
            'order_id': order.order_id, 'merchant_id': 1549901,
            'order_status': 'approved', 'amount': '40000', 'currency': 'GEL',
            'payment_id': 999556,
        }
        payload['signature'] = 'not_a_valid_signature'
        mock_post.return_value.json.return_value = {'response': payload}
        action = admin.site._registry[PaymentOrder]
        with patch.object(action, 'message_user'):
            action.sync_with_flitt_action(None, PaymentOrder.objects.filter(pk=order.pk))
            payload['amount'] = '100'
            payload['signature'] = generate_flitt_signature(payload, secret_key='test')
            action.sync_with_flitt_action(None, PaymentOrder.objects.filter(pk=order.pk))
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.PROCESSING)
        self.assertFalse(UserCourseAccess.objects.filter(user=self.user, course=self.course).exists())

    def test_course_access_grants_course_detail_permission(self):
        course = Course.objects.create(
            title='VIII კლასის მათემატიკა',
            grade='VIII',
            short_description='Short',
            long_description='Long',
            instructor_name='გიორგი',
            duration='30 სთ',
            lessons_count=10,
            video_url='https://youtube.com/embed/test',
            price=Decimal('50.00'),
        )
        # Grant course-specific access
        UserCourseAccess.grant_or_renew_access(
            user=self.user,
            course=course,
            plan_type=PlanType.MONTHLY,
        )
        self.client.force_login(self.user)
        res = self.client.get(reverse('course_detail', kwargs={'pk': course.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.context['has_access'])

    def test_recurring_callback_with_parent_order_id(self):
        initial_order = PaymentOrder.objects.create(
            order_id='MM_PARENT_ORIGINAL_001',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            is_subscription=True,
            status=OrderStatus.APPROVED,
        )
        # Set up current access that expires in 2 days
        access = UserCourseAccess.objects.create(
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=True,
            starts_at=timezone.now() - timedelta(days=28),
            expires_at=timezone.now() + timedelta(days=2),
            last_order=initial_order,
        )
        old_expiry = access.expires_at

        # Webhook for Month 2 recurring charge
        child_params = {
            'order_id': 'FLITT_REC_CHILD_9999',
            'parent_order_id': initial_order.order_id,
            'merchant_id': 1549901,
            'amount': '5000',
            'currency': 'GEL',
            'order_status': 'approved',
            'response_status': 'success',
            'payment_id': 999888777,
        }
        child_params['signature'] = generate_flitt_signature(child_params, secret_key='test')

        res = self.client.post(reverse('payments:flitt_callback'), data=child_params, content_type='application/json')
        self.assertEqual(res.status_code, 200)

        # Renewal order created
        renewal_order = PaymentOrder.objects.filter(order_id='FLITT_REC_CHILD_9999').first()
        self.assertIsNotNone(renewal_order)
        self.assertEqual(renewal_order.status, OrderStatus.APPROVED)

        # Access extended by a calendar month from the prior expiry.
        access.refresh_from_db()
        self.assertAlmostEqual(access.expires_at.timestamp(), add_calendar_months(old_expiry).timestamp(), delta=5)

    def test_pending_subscription_keeps_course_access_until_verified_result(self):
        root = PaymentOrder.objects.create(
            order_id='MM_PENDING_ROOT', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.APPROVED,
        )
        access = UserCourseAccess.objects.create(
            user=self.user, course=self.course, plan_type=PlanType.MONTHLY,
            auto_renew=True, is_active=True, last_order=root,
            starts_at=timezone.now() - timedelta(days=35),
            expires_at=timezone.now() - timedelta(days=1),
            subscription_order_id=root.order_id,
        )
        self.assertTrue(access.is_valid_now())
        self.client.force_login(self.user)
        self.assertTrue(self.client.get(reverse('course_detail', kwargs={'pk': self.course.pk})).context['has_access'])
        self.assertIn(self.course.pk, self.client.get(reverse('home')).context['user_purchased_course_ids'])
        self.assertIn(self.course, self.client.get(reverse('home')).context['paid_courses'])
        self.assertTrue(self.client.get(reverse('payments:pricing') + f'?course_id={self.course.pk}').context['course_access'].is_valid_now())

        child = {
            'order_id': 'MM_FAILED_CHILD', 'parent_order_id': root.order_id,
            'merchant_id': 1549901, 'amount': '5000', 'currency': 'GEL',
            'order_status': 'declined', 'payment_id': 555666,
        }
        child['signature'] = generate_flitt_signature(child, secret_key='test')
        callback_url = reverse('payments:flitt_callback')
        self.assertEqual(self.client.post(callback_url, data=child, content_type='application/json').status_code, 200)
        access.refresh_from_db()
        self.assertIsNotNone(access.renewal_failed_at)
        self.assertFalse(access.is_valid_now())
        self.assertFalse(self.client.get(reverse('course_detail', kwargs={'pk': self.course.pk})).context['has_access'])
        self.assertNotIn(self.course.pk, self.client.get(reverse('home')).context['user_purchased_course_ids'])

        child['order_status'] = 'approved'
        child['signature'] = generate_flitt_signature(child, secret_key='test')
        self.assertEqual(self.client.post(callback_url, data=child, content_type='application/json').status_code, 200)
        access.refresh_from_db()
        self.assertIsNone(access.renewal_failed_at)
        self.assertTrue(access.is_valid_now())
        self.assertTrue(self.client.get(reverse('course_detail', kwargs={'pk': self.course.pk})).context['has_access'])

        child['order_status'] = 'declined'
        child['signature'] = generate_flitt_signature(child, secret_key='test')
        self.assertEqual(self.client.post(callback_url, data=child, content_type='application/json').status_code, 200)
        access.refresh_from_db()
        self.assertIsNone(access.renewal_failed_at)

    def test_processing_and_expired_orders_do_not_count_as_failed_renewals(self):
        root = PaymentOrder.objects.create(
            order_id='MM_WAITING_ROOT', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.APPROVED,
        )
        access = UserCourseAccess.objects.create(
            user=self.user, course=self.course, plan_type=PlanType.MONTHLY,
            auto_renew=True, subscription_order_id=root.order_id,
            expires_at=timezone.now() - timedelta(days=1),
        )
        for status in ('processing', 'expired'):
            payload = {
                'order_id': 'MM_WAITING_CHILD', 'parent_order_id': root.order_id,
                'merchant_id': 1549901, 'amount': '5000', 'currency': 'GEL',
                'order_status': status, 'payment_id': 661122,
            }
            payload['signature'] = generate_flitt_signature(payload, secret_key='test')
            self.assertEqual(self.client.post(
                reverse('payments:flitt_callback'), data=payload, content_type='application/json'
            ).status_code, 200)
            access.refresh_from_db()
            self.assertIsNone(access.renewal_failed_at)
            self.assertTrue(access.is_valid_now())

    def test_failed_renewal_preserves_remaining_paid_time(self):
        root = PaymentOrder.objects.create(
            order_id='MM_EARLY_FAILURE', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.APPROVED,
        )
        access = UserCourseAccess.objects.create(
            user=self.user, course=self.course, plan_type=PlanType.MONTHLY,
            auto_renew=True, subscription_order_id=root.order_id,
            expires_at=timezone.now() + timedelta(days=2),
        )
        self.assertTrue(UserCourseAccess.record_failed_renewal(
            user=self.user, course=self.course, root_order_id=root.order_id,
        ))
        access.refresh_from_db()
        self.assertTrue(access.is_valid_now())
        with patch('payments.models.timezone.now', return_value=access.expires_at + timedelta(seconds=1)):
            self.assertFalse(access.is_valid_now())

    def test_expired_yearly_and_unlinked_monthly_access_still_end(self):
        access = UserCourseAccess.objects.create(
            user=self.user, course=self.course, plan_type=PlanType.MONTHLY,
            auto_renew=True, expires_at=timezone.now() - timedelta(days=1),
        )
        self.assertFalse(access.is_valid_now())
        access.plan_type = PlanType.YEARLY
        access.auto_renew = False
        access.save(update_fields=['plan_type', 'auto_renew'])
        self.assertFalse(access.is_valid_now())

    def test_subscription_schedule_end_and_cancellation_bound_pending_access(self):
        root = PaymentOrder.objects.create(
            order_id='MM_FINITE_ROOT', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.APPROVED,
        )
        access = UserCourseAccess.objects.create(
            user=self.user, course=self.course, plan_type=PlanType.MONTHLY,
            auto_renew=True, subscription_order_id=root.order_id,
            starts_at=root.created_at, expires_at=root.created_at + timedelta(days=30),
        )
        with patch('payments.models.timezone.now', return_value=add_calendar_months(root.created_at, 12)):
            self.assertTrue(access.is_valid_now())
        with patch('payments.models.timezone.now', return_value=add_calendar_months(root.created_at, 14)):
            self.assertFalse(access.is_valid_now())
        root.subscription_canceled_at = timezone.now()
        root.save(update_fields=['subscription_canceled_at'])
        with patch('payments.models.timezone.now', return_value=add_calendar_months(root.created_at, 2)):
            self.assertFalse(access.is_valid_now())

    @patch('payments.flitt_service.requests.post')
    def test_admin_sync_records_known_child_decline(self, mock_post):
        root = PaymentOrder.objects.create(
            order_id='MM_ADMIN_FAILED_ROOT', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.APPROVED,
        )
        child = PaymentOrder.objects.create(
            order_id='MM_ADMIN_FAILED_CHILD', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.PROCESSING,
            subscription_parent_order_id=root.order_id,
        )
        access = UserCourseAccess.objects.create(
            user=self.user, course=self.course, plan_type=PlanType.MONTHLY,
            auto_renew=True, subscription_order_id=root.order_id,
            expires_at=timezone.now() - timedelta(days=1),
        )
        payload = {
            'order_id': child.order_id, 'parent_order_id': root.order_id,
            'merchant_id': 1549901, 'order_status': 'declined',
            'amount': '5000', 'currency': 'GEL',
        }
        payload['signature'] = generate_flitt_signature(payload, secret_key='test')
        mock_post.return_value.json.return_value = {'response': payload}
        action = admin.site._registry[PaymentOrder]
        with patch.object(action, 'message_user'):
            action.sync_with_flitt_action(None, PaymentOrder.objects.filter(pk=child.pk))
        access.refresh_from_db()
        self.assertIsNotNone(access.renewal_failed_at)
        self.assertFalse(access.is_valid_now())

    @patch('payments.flitt_service.requests.post')
    def test_admin_sync_child_approval_keeps_subscription_root(self, mock_post):
        root = PaymentOrder.objects.create(
            order_id='MM_SYNC_RENEWAL_ROOT', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.APPROVED,
        )
        child = PaymentOrder.objects.create(
            order_id='MM_SYNC_RENEWAL_CHILD', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.PROCESSING,
            subscription_parent_order_id=root.order_id,
        )
        payload = {
            'order_id': child.order_id, 'merchant_id': 1549901,
            'amount': '5000', 'currency': 'GEL', 'order_status': 'approved',
            'payment_id': 992233,
        }
        payload['signature'] = generate_flitt_signature(payload, secret_key='test')
        mock_post.return_value.json.return_value = {'response': payload}
        action = admin.site._registry[PaymentOrder]
        with patch.object(action, 'message_user'):
            action.sync_with_flitt_action(None, PaymentOrder.objects.filter(pk=child.pk))
        access = UserCourseAccess.objects.get(user=self.user, course=self.course)
        self.assertEqual(access.subscription_order_id, root.order_id)
        self.assertEqual(access.last_order, child)

    def test_month_end_access_uses_calendar_months(self):
        january_31 = datetime(2025, 1, 31, 12, tzinfo=datetime_timezone.utc)
        with patch('payments.models.timezone.now', return_value=january_31):
            access = UserCourseAccess.grant_or_renew_access(
                user=self.user, course=self.course, plan_type=PlanType.MONTHLY
            )
        self.assertEqual(access.expires_at, datetime(2025, 2, 28, 12, tzinfo=datetime_timezone.utc))
        with patch('payments.models.timezone.now', return_value=datetime(2025, 2, 27, 12, tzinfo=datetime_timezone.utc)):
            UserCourseAccess.grant_or_renew_access(user=self.user, course=self.course, plan_type=PlanType.MONTHLY)
        access.refresh_from_db()
        self.assertEqual(access.expires_at, datetime(2025, 3, 31, 12, tzinfo=datetime_timezone.utc))
        with patch('payments.models.timezone.now', return_value=datetime(2025, 3, 30, 12, tzinfo=datetime_timezone.utc)):
            UserCourseAccess.grant_or_renew_access(user=self.user, course=self.course, plan_type=PlanType.MONTHLY)
        access.refresh_from_db()
        self.assertEqual(access.expires_at, datetime(2025, 4, 30, 12, tzinfo=datetime_timezone.utc))

    @patch.object(FlittPaymentClient, 'cancel_subscription')
    def test_expired_access_still_allows_subscription_cancellation(self, mock_cancel):
        mock_cancel.return_value = {'response_status': 'success', 'status': 'disabled'}
        root = PaymentOrder.objects.create(
            order_id='MM_EXPIRED_CANCEL', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.APPROVED,
        )
        access = UserCourseAccess.objects.create(
            user=self.user, course=self.course, plan_type=PlanType.MONTHLY,
            auto_renew=True, is_active=True,
            expires_at=timezone.now() - timedelta(days=1),
            last_order=root, subscription_order_id=root.order_id,
        )
        self.client.force_login(self.user)
        pricing_url = reverse('payments:pricing') + f'?course_id={self.course.id}'
        self.assertContains(self.client.get(pricing_url), 'action="/payments/cancel-subscription/"')
        res = self.client.post(reverse('payments:cancel_subscription'), data={'course_id': self.course.id})
        self.assertEqual(res.status_code, 302)
        mock_cancel.assert_called_once_with(root.order_id)
        access.refresh_from_db()
        root.refresh_from_db()
        self.assertFalse(access.auto_renew)
        self.assertFalse(access.is_valid_now())
        self.assertIsNotNone(root.subscription_canceled_at)
        self.assertNotContains(self.client.get(pricing_url), 'გამოწერის შეჩერება Flitt-ში')

    @patch.object(FlittPaymentClient, 'cancel_subscription')
    def test_missing_callback_still_allows_subscription_cancellation(self, mock_cancel):
        mock_cancel.return_value = {'response_status': 'success', 'status': 'disabled'}
        root = PaymentOrder.objects.create(
            order_id='MM_MISSING_CALLBACK', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.PROCESSING,
            checkout_url='https://pay.flitt.com/checkout/test',
        )
        self.client.force_login(self.user)
        pricing_url = reverse('payments:pricing') + f'?course_id={self.course.id}'
        pricing = self.client.get(pricing_url)
        self.assertContains(pricing, 'ამ კურსის გამოწერის გადახდა ჩვენს სისტემაში ჯერ არ არის დადასტურებული.')
        self.assertNotContains(pricing, 'დადასტურებული გამოწერა შესაძლოა Flitt-ში კვლავ აქტიური იყოს.')
        self.assertContains(pricing, 'გამოწერის შეჩერება Flitt-ში')
        res = self.client.post(reverse('payments:cancel_subscription'), data={'course_id': self.course.id})
        self.assertEqual(res.status_code, 302)
        mock_cancel.assert_called_once_with(root.order_id)
        root.refresh_from_db()
        self.assertIsNotNone(root.subscription_canceled_at)
        self.assertFalse(UserCourseAccess.objects.filter(user=self.user, course=self.course).exists())
        self.assertNotContains(self.client.get(pricing_url), 'გამოწერის შეჩერება Flitt-ში')

        payload = {
            'order_id': root.order_id, 'merchant_id': 1549901,
            'amount': '5000', 'currency': 'GEL', 'order_status': 'approved',
            'payment_id': 998877,
        }
        payload['signature'] = generate_flitt_signature(payload, secret_key='test')
        self.assertEqual(self.client.post(
            reverse('payments:flitt_callback'), data=payload, content_type='application/json'
        ).status_code, 200)
        access = UserCourseAccess.objects.get(user=self.user, course=self.course)
        self.assertTrue(access.is_valid_now())
        self.assertFalse(access.auto_renew)

    @patch.object(FlittPaymentClient, 'cancel_subscription')
    def test_cancellation_stops_all_checkout_roots_for_course(self, mock_cancel):
        mock_cancel.return_value = {'response_status': 'success', 'status': 'disabled'}
        roots = [PaymentOrder.objects.create(
            order_id=f'MM_MULTI_ROOT_{number}', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True,
            status=OrderStatus.APPROVED if number == 1 else OrderStatus.PROCESSING,
            checkout_url='https://pay.flitt.com/checkout/test',
        ) for number in (1, 2)]
        access = UserCourseAccess.objects.create(
            user=self.user, course=self.course, plan_type=PlanType.MONTHLY,
            auto_renew=True, expires_at=timezone.now() + timedelta(days=10),
            subscription_order_id=roots[0].order_id,
        )
        self.client.force_login(self.user)
        self.client.post(reverse('payments:cancel_subscription'), data={'course_id': self.course.id})
        self.assertEqual(mock_cancel.call_count, 2)
        self.assertEqual({call.args[0] for call in mock_cancel.call_args_list}, {root.order_id for root in roots})
        access.refresh_from_db()
        self.assertFalse(access.auto_renew)
        for root in roots:
            root.refresh_from_db()
            self.assertIsNotNone(root.subscription_canceled_at)

    @patch.object(FlittPaymentClient, 'cancel_subscription')
    def test_partial_cancellation_retries_only_unconfirmed_roots(self, mock_cancel):
        roots = [PaymentOrder.objects.create(
            order_id=f'MM_PARTIAL_{number}', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            is_subscription=True, status=OrderStatus.APPROVED,
            checkout_url='https://pay.flitt.com/checkout/test',
        ) for number in (1, 2)]
        access = UserCourseAccess.objects.create(
            user=self.user, course=self.course, plan_type=PlanType.MONTHLY,
            auto_renew=True, expires_at=timezone.now() + timedelta(days=10),
            subscription_order_id=roots[0].order_id,
        )
        mock_cancel.side_effect = [
            {'response_status': 'success', 'status': 'disabled'},
            {'response_status': 'success', 'status': 'active'},
        ]
        self.client.force_login(self.user)
        url = reverse('payments:cancel_subscription')
        self.client.post(url, data={'course_id': self.course.id})
        confirmed = PaymentOrder.objects.get(order_id=mock_cancel.call_args_list[0].args[0])
        unresolved = PaymentOrder.objects.get(order_id=mock_cancel.call_args_list[1].args[0])
        confirmed.refresh_from_db()
        self.assertIsNotNone(confirmed.subscription_canceled_at)
        access.refresh_from_db()
        self.assertTrue(access.auto_renew)
        self.assertContains(
            self.client.get(reverse('payments:pricing') + f'?course_id={self.course.id}'),
            'action="/payments/cancel-subscription/"',
        )
        mock_cancel.reset_mock()
        mock_cancel.side_effect = None
        mock_cancel.return_value = {'response_status': 'success', 'status': 'disabled'}
        self.client.post(url, data={'course_id': self.course.id})
        mock_cancel.assert_called_once_with(unresolved.order_id)
        access.refresh_from_db()
        self.assertFalse(access.auto_renew)

    @patch.object(FlittPaymentClient, 'cancel_subscription')
    def test_cancellation_is_bounded_and_late_approval_keeps_stopped_root_off(self, mock_cancel):
        roots = [PaymentOrder.objects.create(
            order_id=f'MM_BOUNDED_{number}', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            is_subscription=True, status=OrderStatus.PROCESSING,
            checkout_url='https://pay.flitt.com/checkout/test',
        ) for number in range(5)]
        mock_cancel.return_value = {'response_status': 'success', 'status': 'disabled'}
        self.client.force_login(self.user)
        url = reverse('payments:cancel_subscription')
        self.client.post(url, data={'course_id': self.course.id})
        self.assertEqual(mock_cancel.call_count, 3)
        stopped = PaymentOrder.objects.get(order_id=mock_cancel.call_args_list[0].args[0])
        payload = {'order_id': stopped.order_id, 'merchant_id': 1549901,
                   'amount': '5000', 'currency': 'GEL', 'order_status': 'approved',
                   'payment_id': 8001}
        payload['signature'] = generate_flitt_signature(payload, secret_key='test')
        self.client.post(reverse('payments:flitt_callback'), data=payload, content_type='application/json')
        access = UserCourseAccess.objects.get(user=self.user, course=self.course)
        self.assertFalse(access.auto_renew)
        self.assertContains(
            self.client.get(reverse('payments:pricing') + f'?course_id={self.course.id}'),
            'გამოწერის შეჩერება Flitt-ში',
        )
        self.client.post(url, data={'course_id': self.course.id})
        self.assertEqual(mock_cancel.call_count, 5)
        access.refresh_from_db()
        self.assertFalse(access.auto_renew)
        self.assertEqual(PaymentOrder.objects.filter(
            order_id__in=[root.order_id for root in roots],
            subscription_canceled_at__isnull=True,
        ).count(), 0)

    def test_pricing_only_warns_about_approved_subscription_for_selected_course(self):
        other_course = Course.objects.create(
            title='Other course', grade='VII', short_description='Short',
            long_description='Long', instructor_name='Teacher', duration='30 h',
            lessons_count=1, video_url='https://youtube.com/embed/test',
            price=Decimal('50.00'),
        )
        for course, status in ((self.course, OrderStatus.APPROVED),
                               (other_course, OrderStatus.PROCESSING)):
            PaymentOrder.objects.create(
                order_id=f'MM_PRICING_{course.pk}', user=self.user, course=course,
                plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'),
                amount_tetri=5000, is_subscription=True, status=status,
                checkout_url='https://pay.flitt.com/checkout/test',
            )
        self.client.force_login(self.user)
        approved_page = self.client.get(reverse('payments:pricing') + f'?course_id={self.course.pk}')
        self.assertContains(approved_page, 'დადასტურებული გამოწერა შესაძლოა Flitt-ში კვლავ აქტიური იყოს.')
        pending_page = self.client.get(reverse('payments:pricing') + f'?course_id={other_course.pk}')
        self.assertContains(pending_page, 'ამ კურსის გამოწერის გადახდა ჩვენს სისტემაში ჯერ არ არის დადასტურებული.')
        self.assertNotContains(pending_page, 'დადასტურებული გამოწერა შესაძლოა Flitt-ში კვლავ აქტიური იყოს.')
        self.assertContains(pending_page, 'გამოწერის შეჩერება Flitt-ში')

    def test_new_subscription_replaces_canceled_root(self):
        old_root = PaymentOrder.objects.create(
            order_id='MM_OLD_ROOT', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.APPROVED,
            subscription_canceled_at=timezone.now(),
        )
        new_root = PaymentOrder.objects.create(
            order_id='MM_NEW_ROOT', user=self.user, course=self.course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.APPROVED,
        )
        UserCourseAccess.objects.create(
            user=self.user, course=self.course, plan_type=PlanType.MONTHLY,
            expires_at=timezone.now() - timedelta(days=1), auto_renew=False,
            subscription_order_id=old_root.order_id, last_order=old_root,
        )
        access = UserCourseAccess.grant_or_renew_access(
            user=self.user, course=self.course, plan_type=PlanType.MONTHLY,
            payment_order=new_root, subscription_order_id=new_root.order_id,
        )
        self.assertEqual(access.subscription_order_id, new_root.order_id)
        self.assertTrue(access.auto_renew)
        self.assertTrue(access.is_valid_now())

    @patch.object(FlittPaymentClient, 'cancel_subscription')
    def test_cancellation_never_targets_another_course(self, mock_cancel):
        other_course = Course.objects.create(
            title='Another', grade='VII', short_description='Short', long_description='Long',
            instructor_name='Teacher', duration='30 h', lessons_count=1,
            video_url='https://youtube.com/embed/test', price=Decimal('50.00'),
        )
        root = PaymentOrder.objects.create(
            order_id='MM_OTHER_COURSE', user=self.user, course=other_course,
            plan_type=PlanType.MONTHLY, amount_gel=Decimal('50.00'), amount_tetri=5000,
            currency='GEL', is_subscription=True, status=OrderStatus.APPROVED,
        )
        UserCourseAccess.objects.create(
            user=self.user, course=other_course, plan_type=PlanType.MONTHLY,
            auto_renew=True, expires_at=timezone.now() + timedelta(days=10),
            subscription_order_id=root.order_id,
        )
        self.client.force_login(self.user)
        self.client.post(reverse('payments:cancel_subscription'), data={'course_id': self.course.id})
        mock_cancel.assert_not_called()

    @patch.object(FlittPaymentClient, 'cancel_subscription')
    def test_cancel_subscription_view(self, mock_cancel):
        mock_cancel.return_value = {'response_status': 'success', 'status': 'disabled'}
        order = PaymentOrder.objects.create(
            order_id='MM_SUB_TO_CANCEL',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            is_subscription=True,
            status=OrderStatus.APPROVED,
        )
        access = UserCourseAccess.objects.create(
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=True,
            starts_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
            last_order=order,
            subscription_order_id='MM_SUB_TO_CANCEL',
        )
        self.client.force_login(self.user)
        res = self.client.post(reverse('payments:cancel_subscription'), data={'course_id': self.course.id})
        self.assertEqual(res.status_code, 302)
        mock_cancel.assert_called_once_with('MM_SUB_TO_CANCEL')
        access.refresh_from_db()
        self.assertFalse(access.auto_renew)
        self.assertTrue(access.is_active)
        self.assertTrue(access.is_valid_now())

    @patch.object(FlittPaymentClient, 'cancel_subscription')
    def test_cancel_uses_root_subscription_order_not_renewal_child(self, mock_cancel):
        mock_cancel.return_value = {'response_status': 'success', 'status': 'disabled'}
        root_order = PaymentOrder.objects.create(
            order_id='MM_SUB_ROOT_001',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            is_subscription=True,
            status=OrderStatus.APPROVED,
        )
        renewal_order = PaymentOrder.objects.create(
            order_id='MM_SUB_RENEWAL_002',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            is_subscription=True,
            status=OrderStatus.APPROVED,
        )
        access = UserCourseAccess.objects.create(
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=True,
            starts_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
            last_order=renewal_order,
            subscription_order_id='MM_SUB_ROOT_001',
        )
        self.client.force_login(self.user)
        res = self.client.post(reverse('payments:cancel_subscription'), data={'course_id': self.course.id})
        self.assertEqual(res.status_code, 302)
        mock_cancel.assert_called_once_with('MM_SUB_ROOT_001')
        access.refresh_from_db()
        self.assertFalse(access.auto_renew)

    @patch.object(FlittPaymentClient, 'cancel_subscription')
    def test_cancel_does_not_succeed_on_response_status_only(self, mock_cancel):
        mock_cancel.return_value = {'response_status': 'success', 'status': 'active'}
        order = PaymentOrder.objects.create(
            order_id='MM_SUB_FALSE_CANCEL',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            is_subscription=True,
            status=OrderStatus.APPROVED,
        )
        access = UserCourseAccess.objects.create(
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=True,
            starts_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
            last_order=order,
            subscription_order_id=order.order_id,
        )
        self.client.force_login(self.user)
        res = self.client.post(reverse('payments:cancel_subscription'), data={'course_id': self.course.id})
        self.assertEqual(res.status_code, 302)
        access.refresh_from_db()
        self.assertTrue(access.auto_renew)

    def test_form_urlencoded_callback_parsing(self):
        order = PaymentOrder.objects.create(
            order_id='MM_FORM_ENCODED_001',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            is_subscription=True,
            status=OrderStatus.PROCESSING,
        )
        params = {
            'order_id': order.order_id,
            'merchant_id': 1549901,
            'amount': '5000',
            'currency': 'GEL',
            'order_status': 'approved',
            'response_status': 'success',
        }
        params['signature'] = generate_flitt_signature(params, secret_key='test')

        res = self.client.post(reverse('payments:flitt_callback'), data=params)
        self.assertEqual(res.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.APPROVED)

    def test_callback_rejects_amount_and_currency_mismatch(self):
        order = PaymentOrder.objects.create(
            order_id='MM_MISMATCH_001',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            status=OrderStatus.PROCESSING,
        )
        # 1. Amount mismatch (e.g. 100 tetri instead of 5000)
        bad_amount = {
            'order_id': order.order_id,
            'merchant_id': 1549901,
            'amount': '100',
            'currency': 'GEL',
            'order_status': 'approved',
            'response_status': 'success',
        }
        bad_amount['signature'] = generate_flitt_signature(bad_amount, secret_key='test')
        res1 = self.client.post(reverse('payments:flitt_callback'), data=bad_amount, content_type='application/json')
        self.assertEqual(res1.status_code, 400)
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.PROCESSING)

        # 2. Currency mismatch (e.g. USD instead of GEL)
        bad_curr = {
            'order_id': order.order_id,
            'merchant_id': 1549901,
            'amount': '5000',
            'currency': 'USD',
            'order_status': 'approved',
            'response_status': 'success',
        }
        bad_curr['signature'] = generate_flitt_signature(bad_curr, secret_key='test')
        res2 = self.client.post(reverse('payments:flitt_callback'), data=bad_curr, content_type='application/json')
        self.assertEqual(res2.status_code, 400)
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.PROCESSING)

    def test_payment_response_view_cannot_grant_access_via_forged_post(self):
        order = PaymentOrder.objects.create(
            order_id='MM_FORGE_001',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            status=OrderStatus.PROCESSING,
        )
        # Malicious user attempts forged POST to response view with order_status=approved
        res = self.client.post(reverse('payments:payment_response'), data={
            'order_id': order.order_id,
            'order_status': 'approved',
        })
        self.assertEqual(res.status_code, 200)
        order.refresh_from_db()
        # Order MUST remain PROCESSING - passive view never fulfills!
        self.assertEqual(order.status, OrderStatus.PROCESSING)
        self.assertFalse(UserCourseAccess.objects.filter(user=self.user, course=self.course).exists())

    @patch.object(FlittPaymentClient, 'cancel_subscription')
    def test_cancel_subscription_fails_safely_when_gateway_fails(self, mock_cancel):
        mock_cancel.return_value = {'response_status': 'error', 'error_message': 'Network timeout'}
        order = PaymentOrder.objects.create(
            order_id='MM_SUB_CANCEL_FAIL',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            is_subscription=True,
            status=OrderStatus.APPROVED,
        )
        access = UserCourseAccess.objects.create(
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=True,
            starts_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
            last_order=order,
        )
        self.client.force_login(self.user)
        res = self.client.post(reverse('payments:cancel_subscription'), data={'course_id': self.course.id})
        self.assertEqual(res.status_code, 302)
        access.refresh_from_db()
        # auto_renew MUST remain True because gateway call failed!
        self.assertTrue(access.auto_renew)

    def test_checkout_init_fails_safely_when_course_not_found(self):
        self.client.force_login(self.user)
        # Post non-existent course_id
        res = self.client.post(
            reverse('payments:checkout_init', kwargs={'plan_type': 'monthly'}),
            data={'course_id': 999999}
        )
        self.assertEqual(res.status_code, 302)
        # Ensure no orders were created
        self.assertFalse(PaymentOrder.objects.filter(order_id__startswith='MM_C999999').exists())

    @patch.object(FlittPaymentClient, 'create_checkout_session')
    def test_checkout_blocked_when_user_has_active_access(self, mock_flitt):
        mock_flitt.return_value = {
            'response_status': 'success',
            'checkout_url': 'https://pay.flitt.com/checkout/should_not_open',
        }
        UserCourseAccess.objects.create(
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            is_active=True,
            auto_renew=True,
            starts_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=20),
        )
        self.client.force_login(self.user)
        res = self.client.post(
            reverse('payments:checkout_init', kwargs={'plan_type': 'monthly'}),
            data={'course_id': self.course.id},
        )
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('payments:pricing'))
        mock_flitt.assert_not_called()
        self.assertFalse(
            PaymentOrder.objects.filter(user=self.user, status=OrderStatus.PROCESSING).exists()
        )

    def test_fulfill_access_if_needed_is_idempotent(self):
        order = PaymentOrder.objects.create(
            order_id='MM_FULFILL_IDEM',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            is_subscription=True,
            status=OrderStatus.APPROVED,
            flitt_payment_id='111222333',
        )
        self.assertTrue(order.fulfill_access_if_needed(payment_id='111222333'))
        access = UserCourseAccess.objects.get(user=self.user, course=self.course)
        initial_expiry = access.expires_at
        order.refresh_from_db()
        self.assertIsNotNone(order.access_granted_at)
        self.assertEqual(order.fulfilled_payment_id, '111222333')

        self.assertFalse(order.fulfill_access_if_needed(payment_id='111222333'))
        access.refresh_from_db()
        self.assertEqual(access.expires_at, initial_expiry)

    def test_cancel_subscription_rejects_get_request(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse('payments:cancel_subscription'))
        self.assertEqual(res.status_code, 405)

    def test_out_of_order_delayed_processing_callback_does_not_regress_approved_order(self):
        order = PaymentOrder.objects.create(
            order_id='MM_REGRESS_001',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            status=OrderStatus.APPROVED,
        )
        params = {
            'order_id': order.order_id,
            'merchant_id': 1549901,
            'amount': '5000',
            'currency': 'GEL',
            'order_status': 'processing',
            'response_status': 'success',
        }
        params['signature'] = generate_flitt_signature(params, secret_key='test')
        res = self.client.post(reverse('payments:flitt_callback'), data=params, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        order.refresh_from_db()
        # Must stay APPROVED
        self.assertEqual(order.status, OrderStatus.APPROVED)

        # Also verify delayed 'declined' and 'expired' do not regress APPROVED order
        for late_status in ('declined', 'expired'):
            params['order_status'] = late_status
            params['signature'] = generate_flitt_signature(params, secret_key='test')
            res = self.client.post(reverse('payments:flitt_callback'), data=params, content_type='application/json')
            self.assertEqual(res.status_code, 200)
            order.refresh_from_db()
            self.assertEqual(order.status, OrderStatus.APPROVED)

    def test_recurring_renewal_callback_creates_child_and_renews_access(self):
        parent_order = PaymentOrder.objects.create(
            order_id='MM_PARENT_REC_001',
            user=self.user,
            course=self.course,
            plan_type=PlanType.MONTHLY,
            amount_gel=Decimal('50.00'),
            amount_tetri=5000,
            currency='GEL',
            is_subscription=True,
            status=OrderStatus.APPROVED,
        )
        params = {
            'order_id': 'FLITT_CHILD_001',
            'parent_order_id': parent_order.order_id,
            'merchant_id': 1549901,
            'amount': '5000',
            'currency': 'GEL',
            'order_status': 'approved',
            'response_status': 'success',
            'rectoken': 'rec_child_token',
        }
        params['signature'] = generate_flitt_signature(params, secret_key='test')
        res = self.client.post(reverse('payments:flitt_callback'), data=params, content_type='application/json')
        self.assertEqual(res.status_code, 200)

        child_order = PaymentOrder.objects.filter(order_id='FLITT_CHILD_001').first()
        self.assertIsNotNone(child_order)
        self.assertEqual(child_order.status, OrderStatus.APPROVED)
        self.assertEqual(child_order.course, self.course)
        self.assertTrue(UserCourseAccess.objects.filter(user=self.user, course=self.course, is_active=True).exists())




