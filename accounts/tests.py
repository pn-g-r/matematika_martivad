from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from accounts.forms import CustomUserCreationForm, CustomAuthenticationForm, CustomUserAdminCreationForm, CustomUserAdminChangeForm
from accounts.models import PasswordResetOTP
from accounts.password_reset import SESSION_USER_ID
from accounts.sms import send_otp_sms

User = get_user_model()

class AccountsAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.valid_user_data = {
            'student_name': 'გიორგი მაისურაძე',
            'phone_number': '555111222',
            'parent_name': 'ნინო მაისურაძე',
            'grade': 'VI',
            'book_author': 'გურამ გოგიშვილი',
            'password1': 'StrongPass123!@#',
            'password2': 'StrongPass123!@#',
        }

    def test_successful_registration(self):
        response = self.client.post(reverse('register'), self.valid_user_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(phone_number='555111222').exists())
        user = User.objects.get(phone_number='555111222')
        self.assertEqual(user.username, '555111222')
        self.assertEqual(user.student_name, 'გიორგი მაისურაძე')
        self.assertEqual(user.parent_name, 'ნინო მაისურაძე')
        self.assertEqual(user.grade, 'VI')
        self.assertEqual(user.book_author, 'გურამ გოგიშვილი')
        # Check user is logged in
        self.assertEqual(int(response.context['user'].id), user.id)

    def test_registration_invalid_phone_formats(self):
        invalid_phones = [
            '55511122',         # 8 digits
            '5551112223',       # 10 digits
            '555-111-222',      # dashes
            '+995555111222',    # plus and country code
            '555 111 222',      # spaces
            '55511122a',        # letters
            'abcdefghi',        # non-digits
        ]
        for phone in invalid_phones:
            data = self.valid_user_data.copy()
            data['phone_number'] = phone
            response = self.client.post(reverse('register'), data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(User.objects.filter(phone_number=phone).exists())
            form = response.context['register_form']
            self.assertTrue('phone_number' in form.errors)

    def test_registration_duplicate_phone(self):
        User.objects.create_user(
            username='555111222',
            phone_number='555111222',
            password='ExistingPass123!',
            student_name='დავით ბერიძე',
            parent_name='ანა ბერიძე',
            grade='V',
            book_author='ავტორი'
        )
        response = self.client.post(reverse('register'), self.valid_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['register_form']
        self.assertTrue('phone_number' in form.errors)

    def test_registration_grade_choices(self):
        valid_grades = ['IV', 'V', 'VI', 'VII', 'VIII', 'IX']
        for i, grade in enumerate(valid_grades):
            client = Client()
            data = self.valid_user_data.copy()
            data['phone_number'] = f"55500000{i}"
            data['grade'] = grade
            response = client.post(reverse('register'), data)
            self.assertTrue(User.objects.filter(phone_number=f"55500000{i}").exists())

        # Invalid grade
        client = Client()
        invalid_data = self.valid_user_data.copy()
        invalid_data['phone_number'] = '555999999'
        invalid_data['grade'] = 'X'
        response = client.post(reverse('register'), invalid_data)
        self.assertFalse(User.objects.filter(phone_number='555999999').exists())

    def test_login_successful_with_phone_and_password(self):
        user = User.objects.create_user(
            username='555111222',
            phone_number='555111222',
            password='StrongPass123!@#',
            student_name='გიორგი მაისურაძე',
            parent_name='ნინო მაისურაძე',
            grade='VI',
            book_author='გურამ გოგიშვილი'
        )
        login_data = {
            'phone_number': '555111222',
            'password': 'StrongPass123!@#',
        }
        response = self.client.post(reverse('login'), login_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.context['user'].id), user.id)

    def test_login_invalid_phone_format(self):
        invalid_phones = ['55511122', '5551112223', '555-111-222', 'invalid', '+995555111222']
        for phone in invalid_phones:
            response = self.client.post(reverse('login'), {
                'phone_number': phone,
                'password': 'anypassword',
            })
            self.assertEqual(response.status_code, 200)
            form = response.context['form']
            self.assertTrue('phone_number' in form.errors)

    def test_login_wrong_password(self):
        User.objects.create_user(
            username='555111222',
            phone_number='555111222',
            password='CorrectPassword123!',
            student_name='გიორგი მაისურაძე',
            parent_name='ნინო მაისურაძე',
            grade='VI',
            book_author='გურამ გოგიშვილი'
        )
        response = self.client.post(reverse('login'), {
            'phone_number': '555111222',
            'password': 'WrongPassword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_logout(self):
        User.objects.create_user(
            username='555111222',
            phone_number='555111222',
            password='StrongPass123!@#',
            student_name='გიორგი მაისურაძე',
            parent_name='ნინო მაისურაძე',
            grade='VI',
            book_author='გურამ გოგიშვილი'
        )
        self.client.post(reverse('login'), {
            'phone_number': '555111222',
            'password': 'StrongPass123!@#',
        })
        response = self.client.post(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_superuser_creation_with_classic_fields(self):
        superuser = User.objects.create_superuser(
            username='adminuser',
            email='admin@school.ge',
            password='AdminPassword123!',
            first_name='ადმინ',
            last_name='ადმინიძე'
        )
        self.assertEqual(superuser.username, 'adminuser')
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertEqual(superuser.email, 'admin@school.ge')
        self.assertEqual(superuser.first_name, 'ადმინ')
        self.assertEqual(superuser.last_name, 'ადმინიძე')
        self.assertEqual(superuser.student_name, '')
        self.assertIsNone(superuser.phone_number)

    def test_admin_creation_and_change_forms(self):
        form = CustomUserAdminCreationForm({
            'username': 'staffmember',
            'phone_number': '555222333',
            'first_name': 'ლევან',
            'last_name': 'ბერიძე',
            'email': 'levan@school.ge',
            'password1': 'AdminPassword123!',
            'password2': 'AdminPassword123!',
            'is_staff': True,
            'is_active': True,
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, 'staffmember')
        self.assertEqual(user.phone_number, '555222333')
        self.assertTrue(user.is_staff)

        change_form = CustomUserAdminChangeForm(instance=user)
        self.assertIn('username', change_form.fields)
        self.assertIn('first_name', change_form.fields)
        self.assertIn('email', change_form.fields)
        self.assertIn('student_name', change_form.fields)
        self.assertIn('phone_number', change_form.fields)

    def test_staff_vs_superuser_admin_forms_and_fieldsets(self):
        from accounts.admin import CustomUserAdmin
        from django.contrib.admin.sites import AdminSite
        from django.test import RequestFactory
        from accounts.forms import StaffUserAdminChangeForm

        site = AdminSite()
        cua = CustomUserAdmin(User, site)
        rf = RequestFactory()

        # Staff request
        req_staff = rf.get('/')
        req_staff.user = User(username='staff_admin', is_staff=True, is_superuser=False)

        # Superuser request
        req_super = rf.get('/')
        req_super.user = User(username='super_admin', is_staff=True, is_superuser=True)

        # 1. Add form
        staff_add_form_cls = cua.get_form(req_staff, obj=None)
        super_add_form_cls = cua.get_form(req_super, obj=None)

        staff_add_fields = set(staff_add_form_cls().fields.keys())
        super_add_fields = set(super_add_form_cls().fields.keys())

        expected_staff_fields = {
            'student_name',
            'grade',
            'book_author',
            'parent_name',
            'phone_number',
            'password1',
            'password2',
        }
        self.assertEqual(staff_add_fields, expected_staff_fields)
        self.assertNotIn('username', staff_add_fields)
        self.assertNotIn('is_superuser', staff_add_fields)
        self.assertNotIn('is_staff', staff_add_fields)
        self.assertIn('username', super_add_fields)
        self.assertIn('is_superuser', super_add_fields)

        # 2. Change form
        student_user = User.objects.create_user(
            username='555333444',
            phone_number='555333444',
            password='TestPass123!@#',
            student_name='მოსწავლე 1',
            parent_name='მშობელი 1',
            grade='VII',
            book_author='ავტორი 1'
        )
        staff_change_form_cls = cua.get_form(req_staff, obj=student_user)
        super_change_form_cls = cua.get_form(req_super, obj=student_user)

        staff_change_fields = set(staff_change_form_cls(instance=student_user).fields.keys())
        super_change_fields = set(super_change_form_cls(instance=student_user).fields.keys())

        self.assertNotIn('is_superuser', staff_change_fields)
        self.assertNotIn('is_staff', staff_change_fields)
        self.assertNotIn('groups', staff_change_fields)
        self.assertIn('is_superuser', super_change_fields)
        self.assertIn('groups', super_change_fields)

    def test_staff_registration_view(self):
        # GET request
        response = self.client.get(reverse('staff_register'))
        self.assertEqual(response.status_code, 200)

        # POST request
        staff_data = {
            'username': 'new_staff_member',
            'password1': 'AdminSecret123!@#',
            'password2': 'AdminSecret123!@#',
        }
        post_response = self.client.post(reverse('staff_register'), staff_data, follow=True)
        self.assertEqual(post_response.status_code, 200)
        self.assertTrue(User.objects.filter(username='new_staff_member').exists())
        user = User.objects.get(username='new_staff_member')
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        # Check user is logged in
        self.assertEqual(int(post_response.context['user'].id), user.id)

    def test_admin_change_form_with_none_or_empty_phone(self):
        from accounts.forms import CustomUserAdminChangeForm
        from django.contrib.auth.models import Permission

        staff_user = User.objects.create_user(
            username='admin_without_phone',
            password='AdminPass123!@#',
            is_staff=True,
            phone_number=None,
        )
        perm = Permission.objects.first()
        data = {
            'username': staff_user.username,
            'phone_number': '',
            'date_joined': staff_user.date_joined,
            'is_staff': True,
            'is_active': True,
            'user_permissions': [perm.id] if perm else [],
        }
        form = CustomUserAdminChangeForm(data=data, instance=staff_user)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        self.assertIsNone(saved.phone_number)
        if perm:
            self.assertIn(perm, saved.user_permissions.all())

    def test_admin_changelist_view_renders_correctly(self):
        superuser = User.objects.create_superuser(
            username='super_changelist_test',
            email='super@test.com',
            password='Password123!',
        )
        self.client.force_login(superuser)
        response = self.client.get('/admin/accounts/customuser/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'super_changelist_test')


class PasswordResetOTPTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='555111222',
            phone_number='555111222',
            password='OldPassword123!@#',
            student_name='გიორგი მაისურაძე',
            parent_name='ნინო მაისურაძე',
            grade='VI',
            book_author='გურამ გოგიშვილი',
        )

    def test_login_page_has_forgot_password_link(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('password_reset'))

    def test_password_reset_page_renders(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'პაროლის აღდგენა')

    @patch('accounts.password_reset.send_otp_sms', return_value=(True, None))
    @patch('accounts.password_reset.generate_otp', return_value='123456')
    def test_existing_user_receives_otp_sms(self, _mock_otp, mock_sms):
        response = self.client.post(reverse('password_reset'), {
            'phone_number': '555111222',
        })
        self.assertRedirects(response, reverse('password_reset_verify'))
        mock_sms.assert_called_once_with('555111222', '123456')
        self.assertTrue(
            PasswordResetOTP.objects.filter(phone_number='555111222', is_used=False).exists()
        )

    @patch('accounts.password_reset.send_otp_sms')
    def test_unknown_phone_does_not_send_sms(self, mock_sms):
        response = self.client.post(reverse('password_reset'), {
            'phone_number': '599000000',
        })
        self.assertRedirects(response, reverse('password_reset_verify'))
        mock_sms.assert_not_called()
        self.assertFalse(PasswordResetOTP.objects.filter(phone_number='599000000').exists())

    def test_password_reset_invalid_phone_format(self):
        response = self.client.post(reverse('password_reset'), {
            'phone_number': '55511122',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('phone_number' in response.context['form'].errors)

    @patch('accounts.password_reset.send_otp_sms', return_value=(True, None))
    @patch('accounts.password_reset.generate_otp', return_value='123456')
    def test_full_reset_flow_changes_password_and_logs_in(self, _mock_otp, _mock_sms):
        self.client.post(reverse('password_reset'), {'phone_number': '555111222'})
        verify = self.client.post(reverse('password_reset_verify'), {'code': '123456'})
        self.assertRedirects(verify, reverse('password_reset_confirm'))

        confirm = self.client.post(reverse('password_reset_confirm'), {
            'password1': 'NewStrongPass123!@#',
            'password2': 'NewStrongPass123!@#',
        }, follow=True)
        self.assertEqual(confirm.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPass123!@#'))
        self.assertEqual(int(confirm.context['user'].id), self.user.id)

    @patch('accounts.password_reset.send_otp_sms', return_value=(True, None))
    @patch('accounts.password_reset.generate_otp', return_value='123456')
    def test_wrong_otp_is_rejected(self, _mock_otp, _mock_sms):
        self.client.post(reverse('password_reset'), {'phone_number': '555111222'})
        response = self.client.post(reverse('password_reset_verify'), {'code': '000000'})
        self.assertEqual(response.status_code, 200)
        otp = PasswordResetOTP.objects.get(phone_number='555111222')
        self.assertEqual(otp.attempts, 1)
        self.assertFalse(otp.is_used)

    @patch('accounts.password_reset.send_otp_sms', return_value=(True, None))
    @patch('accounts.password_reset.generate_otp', return_value='123456')
    def test_expired_otp_is_rejected(self, _mock_otp, _mock_sms):
        self.client.post(reverse('password_reset'), {'phone_number': '555111222'})
        otp = PasswordResetOTP.objects.get(phone_number='555111222')
        otp.expires_at = timezone.now() - timedelta(minutes=1)
        otp.save(update_fields=['expires_at'])
        response = self.client.post(reverse('password_reset_verify'), {'code': '123456'})
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.client.session.get(SESSION_USER_ID))

    @patch('accounts.password_reset.send_otp_sms', return_value=(True, None))
    @patch('accounts.password_reset.generate_otp', return_value='123456')
    def test_resend_is_rate_limited(self, _mock_otp, mock_sms):
        self.client.post(reverse('password_reset'), {'phone_number': '555111222'})
        self.assertEqual(mock_sms.call_count, 1)
        response = self.client.post(reverse('password_reset_resend'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_sms.call_count, 1)

    @override_settings(SMS_OFFICE_API_KEY='test-sms-key', SMS_OFFICE_SENDER='MatMartivad')
    @patch('accounts.sms.send_sms')
    def test_send_otp_sms_uses_settings_api_key(self, mock_send):
        mock_send.return_value = {'Success': True, 'ErrorCode': 0}
        ok, err = send_otp_sms('555111222', '123456')
        self.assertTrue(ok)
        self.assertIsNone(err)
        kwargs = mock_send.call_args.kwargs
        self.assertEqual(kwargs['api_key'], 'test-sms-key')
        self.assertEqual(kwargs['destination'], '555111222')
        self.assertEqual(kwargs['sender'], 'MatMartivad')
        self.assertTrue(kwargs['urgent'])
        self.assertIn('123456', kwargs['content'])








