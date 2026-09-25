from django.contrib import admin
from django.utils import timezone
from django.utils.html import mark_safe
from .models import PaymentOrder, UserCourseAccess, PlanType
from .flitt_service import is_flitt_subscription_stopped

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
        'access_granted_at',
        'fulfilled_payment_id',
        'subscription_canceled_at',
        'subscription_parent_order_id',
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
                try:
                    valid_amount = int(status_info.get('amount')) == order.amount_tetri
                except (ValueError, TypeError):
                    valid_amount = False
                if not valid_amount or (status_info.get('currency') or '').upper() != order.currency.upper():
                    self.message_user(request, f"Flitt-ის თანხა ან ვალუტა არ ემთხვევა შეკვეთას {order.order_id}.", level='warning')
                    continue
                remote_status = (status_info.get('order_status') or '').lower()
                remote_parent_id = status_info.get('parent_order_id') or ''
                if (remote_parent_id and remote_parent_id != order.order_id
                        and order.subscription_parent_order_id
                        and remote_parent_id != order.subscription_parent_order_id):
                    self.message_user(request, f"Flitt-ის ძირითადი გამოწერა არ ემთხვევა შეკვეთას {order.order_id}.", level='warning')
                    continue
                if remote_parent_id and remote_parent_id != order.order_id:
                    order.subscription_parent_order_id = remote_parent_id
                parent_id = order.subscription_parent_order_id
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
                        sub_root = (parent_id or order.order_id) if order.is_subscription and order.plan_type == PlanType.MONTHLY else None
                        order.fulfill_access_if_needed(
                            rectoken=rectoken,
                            subscription_order_id=sub_root,
                            payment_id=str(payment_id) if payment_id else order.flitt_payment_id,
                        )
                    updated_count += 1
                elif remote_status in ('declined', 'expired', 'reversed'):
                    previous_status = order.status
                    if previous_status == 'approved' and remote_status in ('declined', 'expired'):
                        continue
                    order.status = remote_status
                    order.save(update_fields=['status', 'subscription_parent_order_id', 'updated_at'])
                    if remote_status == 'declined' and previous_status != 'declined' and parent_id:
                        UserCourseAccess.record_failed_renewal(
                            user=order.user, course=order.course, root_order_id=parent_id,
                        )
        self.message_user(request, f"სინქრონიზაცია დასრულდა. Flitt-ის მიხედვით განახლდა {updated_count} შეკვეთა.")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.status == 'approved' and obj.course:
            sub_root = (obj.subscription_parent_order_id or obj.order_id) if obj.is_subscription and obj.plan_type == PlanType.MONTHLY else None
            obj.fulfill_access_if_needed(subscription_order_id=sub_root)


@admin.register(UserCourseAccess)
class UserCourseAccessAdmin(admin.ModelAdmin):
    list_display = (
        'get_user_display',
        'course',
        'plan_type',
        'get_active_badge',
        'auto_renew',
        'subscription_order_id',
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
        'subscription_order_id',
    )
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-expires_at',)
    actions = ['cancel_subscription_action']

    @admin.action(description="🛑 Flitt გამოწერის გაუქმება (ავტო-განახლების შეწყვეტა)")
    def cancel_subscription_action(self, request, queryset):
        from .flitt_service import FlittPaymentClient
        client = FlittPaymentClient()
        cancelled_count = 0
        failed_count = 0
        for access in queryset:
            sub_order_id = access.get_subscription_order_id()
            if sub_order_id:
                res = client.cancel_subscription(sub_order_id)
                if is_flitt_subscription_stopped(res):
                    PaymentOrder.objects.filter(order_id=sub_order_id, user=access.user).update(
                        subscription_canceled_at=timezone.now()
                    )
                    access.auto_renew = False
                    access.save(update_fields=['auto_renew', 'updated_at'])
                    cancelled_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
        if failed_count:
            self.message_user(
                request,
                f"გამოწერა გაუქმდა {cancelled_count} მომხმარებლისთვის. {failed_count} ჩანაწერზე Flitt-მა disabled არ დაადასტურა.",
                level='warning',
            )
        else:
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


