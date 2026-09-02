from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import (
    CustomUserCreationForm,
    CustomUserAdminCreationForm,
    CustomUserAdminChangeForm,
    StaffUserAdminChangeForm,
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserAdminCreationForm
    form = CustomUserAdminChangeForm

    list_display = (
        'student_name',
        'parent_name',
        'grade',
        'book_author',
        'phone_number',
    )
    list_filter = ('grade', 'is_staff', 'is_superuser', 'is_active')

    superuser_fieldsets = (
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

    staff_fieldsets = (
        ('მოსწავლის ინფორმაცია', {
            'fields': (
                'student_name',
                'grade',
                'book_author',
                'parent_name',
                'phone_number',
                'password',
            )
        }),
    )

    superuser_add_fieldsets = (
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

    staff_add_fieldsets = (
        ('რეგისტრაციის ველები (მოსწავლე და მშობელი)', {
            'classes': ('wide',),
            'fields': (
                'student_name',
                'grade',
                'book_author',
                'parent_name',
                'phone_number',
                'password1',
                'password2',
            ),
        }),
    )

    search_fields = ('student_name', 'parent_name', 'phone_number', 'username', 'email', 'book_author')
    ordering = ('-date_joined',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.get_add_fieldsets(request)
        if request.user.is_superuser:
            return self.superuser_fieldsets
        return self.staff_fieldsets

    def get_add_fieldsets(self, request):
        if request.user.is_superuser:
            return self.superuser_add_fieldsets
        return self.staff_add_fieldsets

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            if not request.user.is_superuser:
                self.add_form = CustomUserCreationForm
            else:
                self.add_form = CustomUserAdminCreationForm
        else:
            if not request.user.is_superuser:
                self.form = StaffUserAdminChangeForm
            else:
                self.form = CustomUserAdminChangeForm
        return super().get_form(request, obj, **kwargs)





