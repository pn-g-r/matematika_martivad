from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.forms import CustomUserCreationForm, CustomAuthenticationForm

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

