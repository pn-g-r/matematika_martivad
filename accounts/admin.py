from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'phone_number',
        'student_name',
        'parent_name',
        'grade',
        'book_author',
        'is_staff',
        'is_active',
    )
    list_filter = ('grade', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('პერსონალური ინფორმაცია', {
            'fields': (
                'student_name',
                'parent_name',
                'grade',
                'book_author',
            )
        }),
        ('უფლებები', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('თარიღები', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number',
                'student_name',
                'parent_name',
                'grade',
                'book_author',
                'password1',
                'password2',
                'is_staff',
                'is_active',
            ),
        }),
    )
    search_fields = ('phone_number', 'student_name', 'parent_name', 'book_author')
    ordering = ('phone_number',)

