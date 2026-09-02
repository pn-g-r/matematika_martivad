from django.contrib import admin
from django.utils.html import mark_safe
from .models import PaymentOrder, UserSubscriptionAccess

@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'get_user_display',
        'plan_type',
        'amount_gel',
        'get_status_badge',
        'is_subscription',
        'masked_card',
        'created_at',
    )
    list_filter = ('status', 'plan_type', 'is_subscription', 'currency', 'created_at')
    search_fields = (
        'order_id',
        'user__username',
        'user__student_name',
        'user__phone_number',
        'flitt_payment_id',
        'masked_card',
    )
    readonly_fields = (
        'order_id',
        'user',
        'plan_type',
        'amount_gel',
        'amount_tetri',
        'currency',
        'order_desc',
        'is_subscription',
        'checkout_url',
        'flitt_payment_id',
        'masked_card',
        'card_type',
        'response_status',
        'response_code',
        'response_description',
        'raw_response',
        'created_at',
        'updated_at',
    )
    ordering = ('-created_at',)

    @admin.display(description="მომხმარებელი")
    def get_user_display(self, obj):
        return obj.user.student_name or obj.user.username

    @admin.display(description="სტატუსი")
    def get_status_badge(self, obj):
        colors = {
            'approved': ('#4ade80', 'rgba(74, 222, 128, 0.2)'),
            'processing': ('#38bdf8', 'rgba(56, 189, 248, 0.2)'),
            'created': ('#cbd5e1', 'rgba(203, 213, 225, 0.2)'),
            'declined': ('#f87171', 'rgba(248, 113, 113, 0.2)'),
            'expired': ('#fbbf24', 'rgba(251, 191, 36, 0.2)'),
            'reversed': ('#c084fc', 'rgba(192, 132, 252, 0.2)'),
        }
        fg, bg = colors.get(obj.status, ('#cbd5e1', 'rgba(203, 213, 225, 0.2)'))
        return mark_safe(
            f'<span style="background: {bg}; color: {fg}; border: 1px solid {fg}; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 11px;">{obj.get_status_display()}</span>'
        )


@admin.register(UserSubscriptionAccess)
class UserSubscriptionAccessAdmin(admin.ModelAdmin):
    list_display = (
        'get_user_display',
        'plan_type',
        'get_active_badge',
        'auto_renew',
        'starts_at',
        'expires_at',
        'created_at',
    )
    list_filter = ('is_active', 'auto_renew', 'plan_type', 'expires_at')
    search_fields = (
        'user__username',
        'user__student_name',
        'user__phone_number',
        'rectoken',
    )
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-expires_at',)

    @admin.display(description="მომხმარებელი")
    def get_user_display(self, obj):
        return obj.user.student_name or obj.user.username

    @admin.display(description="აქტიურობის სტატუსი")
    def get_active_badge(self, obj):
        if obj.is_valid_now():
            return mark_safe(
                '<span style="background: rgba(74, 222, 128, 0.2); color: #4ade80; border: 1px solid #4ade80; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 11px;">აქტიური</span>'
            )
        return mark_safe(
            '<span style="background: rgba(248, 113, 113, 0.2); color: #f87171; border: 1px solid #f87171; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 11px;">ვადაგასული</span>'
        )

