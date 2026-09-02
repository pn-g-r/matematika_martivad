from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\d{9}$',
    message='ტელეფონის ნომერი უნდა შედგებოდეს ზუსტად 9 ციფრისგან (მაგ: 555111222).'
)

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('ტელეფონის ნომერი აუცილებელია.')
        phone_number = str(phone_number).strip()
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None

    CLASS_CHOICES = [
        ('IV', 'IV'),
        ('V', 'V'),
        ('VI', 'VI'),
        ('VII', 'VII'),
        ('VIII', 'VIII'),
        ('IX', 'IX'),
    ]

    student_name = models.CharField(
        max_length=150,
        verbose_name="მოსწავლის სახელი და გვარი"
    )
    phone_number = models.CharField(
        max_length=9,
        unique=True,
        validators=[phone_validator],
        verbose_name="მშობლის ტელეფონის ნომერი"
    )
    parent_name = models.CharField(
        max_length=150,
        verbose_name="მშობლის სახელი და გვარი"
    )
    grade = models.CharField(
        max_length=10,
        choices=CLASS_CHOICES,
        verbose_name="კლასი"
    )
    book_author = models.CharField(
        max_length=150,
        verbose_name="წიგნის ავტორი"
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['student_name', 'parent_name', 'grade', 'book_author']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.student_name} ({self.phone_number})"

