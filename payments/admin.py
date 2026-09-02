from django.contrib import admin
from django.utils.html import mark_safe
from .models import PaymentOrder, UserCourseAccess

@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'get_user_display',
        'course',
        'plan_type',
        'amount_gel',
        'get_status_badge',
        'is_subscription',
        'masked_card',
        'created_at',
    )
    list_filter = ('status', 'course', 'plan_type', 'is_subscription', 'currency', 'created_at')
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

    actions = ['sync_with_flitt_action']

    @admin.action(description="🔄 Flitt-იდან სტატუსის სინქრონიზაცია")
    def sync_with_flitt_action(self, request, queryset):
        from .flitt_service import FlittPaymentClient
        client = FlittPaymentClient()
        updated_count = 0
        for order in queryset:
            status_info = client.get_order_status(order.order_id)
            if status_info:
                remote_status = (status_info.get('order_status') or '').lower()
                rectoken = status_info.get('rectoken', '')
                masked_card = status_info.get('masked_card', '')
                card_type = status_info.get('card_type', '')
                payment_id = status_info.get('payment_id', '')

                if remote_status == 'approved':
                    order.status = 'approved'
                    if masked_card:
                        order.masked_card = masked_card
                    if card_type:
                        order.card_type = card_type
                    if payment_id:
                        order.flitt_payment_id = str(payment_id)
                    order.save()
                    if order.course:
                        UserCourseAccess.grant_or_renew_access(
                            user=order.user,
                            course=order.course,
                            plan_type=order.plan_type,
                            payment_order=order,
                            rectoken=rectoken,
                        )
                    updated_count += 1
                elif remote_status in ('declined', 'expired', 'reversed'):
                    order.status = remote_status
                    order.save(update_fields=['status', 'updated_at'])
        self.message_user(request, f"სინქრონიზაცია დასრულდა. Flitt-ის მიხედვით განახლდა {updated_count} შეკვეთა.")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.status == 'approved' and obj.course:
            UserCourseAccess.grant_or_renew_access(
                user=obj.user,
                course=obj.course,
                plan_type=obj.plan_type,
                payment_order=obj,
            )


@admin.register(UserCourseAccess)
class UserCourseAccessAdmin(admin.ModelAdmin):
    list_display = (
        'get_user_display',
        'course',
        'plan_type',
        'get_active_badge',
        'auto_renew',
        'starts_at',
        'expires_at',
        'created_at',
    )
    list_filter = ('is_active', 'auto_renew', 'course', 'plan_type', 'expires_at')
    search_fields = (
        'user__username',
        'user__student_name',
        'user__phone_number',
        'course__title',
        'rectoken',
    )
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-expires_at',)
    actions = ['cancel_subscription_action']

    @admin.action(description="🛑 Flitt გამოწერის გაუქმება (ავტო-განახლების შეწყვეტა)")
    def cancel_subscription_action(self, request, queryset):
        from .flitt_service import FlittPaymentClient
        client = FlittPaymentClient()
        cancelled_count = 0
        for access in queryset:
            if access.last_order:
                client.cancel_subscription(access.last_order.order_id)
            access.auto_renew = False
            access.save(update_fields=['auto_renew', 'updated_at'])
            cancelled_count += 1
        self.message_user(request, f"გამოწერა წარმატებით გაუქმდა {cancelled_count} მომხმარებლისთვის.")

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


