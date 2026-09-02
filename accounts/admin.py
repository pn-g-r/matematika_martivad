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
        'username',
        'student_name',
        'phone_number',
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
        (None, {'fields': ('username', 'password')}),
        ('პირადი ინფორმაცია (Personal info)', {
            'fields': (
                'first_name',
                'last_name',
                'email',
            )
        }),
        ('მოსწავლის ინფორმაცია (Student info)', {
            'fields': (
                'student_name',
                'phone_number',
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
                'username',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'email',
                'phone_number',
                'student_name',
                'parent_name',
                'grade',
                'book_author',
                'is_staff',
                'is_superuser',
                'is_active',
            ),
        }),
    )
    search_fields = ('username', 'phone_number', 'first_name', 'last_name', 'email', 'student_name', 'parent_name')
    ordering = ('username',)



