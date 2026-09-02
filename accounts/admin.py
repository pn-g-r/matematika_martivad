from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser
from .forms import (
    CustomUserCreationForm,
    CustomUserAdminCreationForm,
    CustomUserAdminChangeForm,
    StaffUserAdminChangeForm,
)

class UserTypeFilter(admin.SimpleListFilter):
    title = 'მომხმარებლის ტიპი'
    parameter_name = 'user_type'

    def lookups(self, request, model_admin):
        return (
            ('students', 'მოსწავლეები'),
            ('staff', 'ადმინისტრატორები (Staff)'),
            ('superusers', 'მთავარი ადმინები (Superusers)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'students':
            return queryset.filter(is_staff=False, is_superuser=False)
        if self.value() == 'staff':
            return queryset.filter(is_staff=True, is_superuser=False)
        if self.value() == 'superusers':
            return queryset.filter(is_superuser=True)
        return queryset

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserAdminCreationForm
    form = CustomUserAdminChangeForm

    list_display = (
        'get_display_name',
        'get_role_badge',
        'parent_name',
        'grade',
        'book_author',
        'get_contact',
    )
    list_filter = (UserTypeFilter, 'grade', 'is_active')

    @admin.display(description="მომხმარებელი / მოსწავლე", ordering='student_name')
    def get_display_name(self, obj):
        if obj.is_superuser:
            full = f"{obj.first_name} {obj.last_name}".strip()
            name_part = f" - {full}" if full else ""
            return format_html(
                '<strong style="color: #c084fc;">🔑 {}</strong><span style="color: #94a3b8; font-size: 12px;">{}</span>',
                obj.username,
                name_part,
            )
        if obj.is_staff:
            full = f"{obj.first_name} {obj.last_name}".strip()
            name_part = f" - {full}" if full else ""
            return format_html(
                '<strong style="color: #38bdf8;">🛡️ {}</strong><span style="color: #94a3b8; font-size: 12px;">{}</span>',
                obj.username,
                name_part,
            )
        return obj.student_name or obj.username

    @admin.display(description="როლი")
    def get_role_badge(self, obj):
        if obj.is_superuser:
            return format_html(
                '<span style="background: rgba(192, 132, 252, 0.2); color: #c084fc; border: 1px solid #c084fc; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 11px;">Superuser</span>'
            )
        if obj.is_staff:
            return format_html(
                '<span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #38bdf8; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 11px;">ადმინი</span>'
            )
        return format_html(
            '<span style="background: rgba(74, 222, 128, 0.2); color: #4ade80; border: 1px solid #4ade80; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 11px;">მოსწავლე</span>'
        )

    @admin.display(description="ტელეფონი / კონტაქტი", ordering='phone_number')
    def get_contact(self, obj):
        if obj.phone_number:
            return obj.phone_number
        if obj.email:
            return obj.email
        return "-"


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





