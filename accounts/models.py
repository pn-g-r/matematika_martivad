from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\d{9}$',
    message='ტელეფონის ნომერი უნდა შედგებოდეს ზუსტად 9 ციფრისგან (მაგ: 555111222).'
)

class CustomUser(AbstractUser):
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
        blank=True,
        default="",
        verbose_name="მოსწავლის სახელი და გვარი"
    )
    phone_number = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        unique=True,
        validators=[phone_validator],
        verbose_name="მშობლის ტელეფონის ნომერი"
    )
    parent_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name="მშობლის სახელი და გვარი"
    )
    grade = models.CharField(
        max_length=10,
        choices=CLASS_CHOICES,
        blank=True,
        default="",
        verbose_name="კლასი"
    )
    book_author = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name="სახელმძღვანელოს ავტორი"
    )

    objects = UserManager()

    def __str__(self):
        if self.student_name:
            return f"{self.student_name} ({self.phone_number or self.username})"
        if self.first_name or self.last_name:
            full = f"{self.first_name} {self.last_name}".strip()
            return f"{full} ({self.username})"
        return self.username


class PasswordResetOTP(models.Model):
    phone_number = models.CharField(max_length=9, db_index=True)
    code_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP {self.phone_number}"


