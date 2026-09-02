import re
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser

PHONE_REGEX = re.compile(r'^\d{9}$')
PHONE_ERROR_MSG = "ტელეფონის ნომერი უნდა შედგებოდეს ზუსტად 9 ციფრისგან (მაგ: 555111222). სხვა სიმბოლოები დაუშვებელია."

class CustomUserCreationForm(forms.ModelForm):
    student_name = forms.CharField(
        label="მოსწავლის სახელი და გვარი",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'მოსწავლის სახელი და გვარი',
            'class': 'form-input',
            'autocomplete': 'name',
        })
    )
    phone_number = forms.CharField(
        label="მშობლის ტელეფონის ნომერი",
        max_length=9,
        min_length=9,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '555111222',
            'class': 'form-input phone-input',
            'pattern': r'\d{9}',
            'inputmode': 'numeric',
            'maxlength': '9',
            'title': 'ზუსტად 9 ციფრი (მაგ: 555111222)',
            'autocomplete': 'tel',
        })
    )
    parent_name = forms.CharField(
        label="მშობლის სახელი და გვარი",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'მშობლის სახელი და გვარი',
            'class': 'form-input',
            'autocomplete': 'name',
        })
    )
    grade = forms.ChoiceField(
        label="კლასი",
        choices=CustomUser.CLASS_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'grade-radio-input',
        }),
        required=True,
    )
    book_author = forms.CharField(
        label="წიგნის ავტორი",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'წიგნის ავტორი',
            'class': 'form-input',
        })
    )
    password1 = forms.CharField(
        label="პაროლი",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'პაროლი',
            'class': 'form-input',
            'autocomplete': 'new-password',
        }),
        required=True,
    )
    password2 = forms.CharField(
        label="პაროლის დადასტურება",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'გაიმეორეთ პაროლი',
            'class': 'form-input',
            'autocomplete': 'new-password',
        }),
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = (
            'student_name',
            'phone_number',
            'parent_name',
            'grade',
            'book_author',
        )

    def clean_student_name(self):
        name = self.cleaned_data.get('student_name', '').strip()
        if not name:
            raise ValidationError("მოსწავლის სახელისა და გვარის შეყვანა სავალდებულოა.")
        return name

    def clean_parent_name(self):
        name = self.cleaned_data.get('parent_name', '').strip()
        if not name:
            raise ValidationError("მშობლის სახელისა და გვარის შეყვანა სავალდებულოა.")
        return name

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if not PHONE_REGEX.match(phone):
            raise ValidationError(PHONE_ERROR_MSG)
        if CustomUser.objects.filter(phone_number=phone).exists():
            raise ValidationError("ამ ტელეფონის ნომრით მომხმარებელი უკვე რეგისტრირებულია.")
        return phone

    def clean_book_author(self):
        author = self.cleaned_data.get('book_author', '').strip()
        if not author:
            raise ValidationError("წიგნის ავტორის შეყვანა სავალდებულოა.")
        return author

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                self.add_error('password2', "პაროლები ერთმანეთს არ ემთხვევა.")
            else:
                user = CustomUser(
                    phone_number=cleaned_data.get('phone_number', ''),
                    student_name=cleaned_data.get('student_name', ''),
                    parent_name=cleaned_data.get('parent_name', ''),
                    grade=cleaned_data.get('grade', ''),
                    book_author=cleaned_data.get('book_author', ''),
                )
                try:
                    validate_password(password1, user)
                except ValidationError as error:
                    self.add_error('password1', error)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(forms.Form):
    phone_number = forms.CharField(
        label="მშობლის ტელეფონის ნომერი",
        max_length=9,
        min_length=9,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '555111222',
            'class': 'form-input phone-input',
            'pattern': r'\d{9}',
            'inputmode': 'numeric',
            'maxlength': '9',
            'title': 'ზუსტად 9 ციფრი (მაგ: 555111222)',
            'autocomplete': 'tel',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="პაროლი",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'პაროლი',
            'class': 'form-input',
            'autocomplete': 'current-password',
        }),
        required=True,
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if not PHONE_REGEX.match(phone):
            raise ValidationError(PHONE_ERROR_MSG)
        return phone

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        password = cleaned_data.get('password')

        if phone_number and password:
            self.user_cache = authenticate(
                self.request,
                phone_number=phone_number,
                username=phone_number,
                password=password
            )
            if self.user_cache is None:
                raise ValidationError(
                    "მითითებული ტელეფონის ნომერი ან პაროლი არასწორია.",
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                "ეს ანგარიში დაბლოკილია.",
                code='inactive',
            )

    def get_user(self):
        return self.user_cache
