from unittest.mock import patch
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import PaymentOrder, UserCourseAccess, PlanType, OrderStatus
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

    def test_pricing_page_renders_successfully(self):
        response = self.client.get(reverse('payments:pricing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '50')
        self.assertContains(response, '400')
        self.assertContains(response, 'ყოველთვიური გამოწერა')
        self.assertContains(response, '1-წლიანი სრული პაკეტი')

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
        self.assertEqual(order.flitt_payment_id, '888777666')
        self.assertEqual(order.masked_card, '444455XXXXXX1111')

        access = UserCourseAccess.objects.get(user=self.user, course=self.course)
        self.assertTrue(access.is_active)
        self.assertTrue(access.is_valid_now())
        self.assertEqual(access.plan_type, PlanType.MONTHLY)
        self.assertEqual(access.rectoken, 'REC_TOKEN_XYZ_999')
        self.assertTrue(access.expires_at > timezone.now() + timedelta(days=28))

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
        self.assertContains(res, reverse('course_detail', kwargs={'pk': course.id}))

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

        # Access extended by 30 days from old_expiry
        access.refresh_from_db()
        self.assertAlmostEqual(access.expires_at.timestamp(), (old_expiry + timedelta(days=30)).timestamp(), delta=5)

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
        )
        self.client.force_login(self.user)
        res = self.client.post(reverse('payments:cancel_subscription'), data={'course_id': self.course.id})
        self.assertEqual(res.status_code, 302)
        mock_cancel.assert_called_once_with('MM_SUB_TO_CANCEL')
        access.refresh_from_db()
        self.assertFalse(access.auto_renew)
        self.assertTrue(access.is_active)
        self.assertTrue(access.is_valid_now())

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




