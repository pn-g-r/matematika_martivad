from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserAdminCreationForm, CustomUserAdminChangeForm

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserAdminCreationForm
    form = CustomUserAdminChangeForm

    list_display = (
        'phone_number',
        'student_name',
        'first_name',
        'last_name',
        'email',
        'grade',
        'is_staff',
        'is_superuser',
        'is_active',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'grade')
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('კლასიკური ინფორმაცია (Classic Info)', {
            'fields': (
                'first_name',
                'last_name',
                'email',
            )
        }),
        ('მოსწავლის ინფორმაცია (Student Info)', {
            'fields': (
                'student_name',
                'parent_name',
                'grade',
                'book_author',
            )
        }),
        ('უფლებები (Permissions)', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('მნიშვნელოვანი თარიღები (Important dates)', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number',
                'first_name',
                'last_name',
                'email',
                'student_name',
                'parent_name',
                'grade',
                'book_author',
                'password1',
                'password2',
                'is_staff',
                'is_superuser',
                'is_active',
            ),
        }),
    )
    search_fields = ('phone_number', 'first_name', 'last_name', 'email', 'student_name', 'parent_name', 'book_author')
    ordering = ('phone_number',)


