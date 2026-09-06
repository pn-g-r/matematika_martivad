import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class PlanType(models.TextChoices):
    MONTHLY = 'monthly', 'ყოველთვიური გამოწერა (50 ₾ / თვე)'
    YEARLY = 'yearly', '1-წლიანი სრული პაკეტი (400 ₾ / წელი)'

class OrderStatus(models.TextChoices):
    CREATED = 'created', 'შექმნილია (Created)'
    PROCESSING = 'processing', 'მუშავდება (Processing)'
    APPROVED = 'approved', 'დამტკიცებულია / გადახდილია (Approved)'
    DECLINED = 'declined', 'უარყოფილია (Declined)'
    EXPIRED = 'expired', 'ვადაგასულია (Expired)'
    REVERSED = 'reversed', 'გაუქმებულია / დაბრუნებულია (Reversed)'

class PaymentOrder(models.Model):
    order_id = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name="შეკვეთის ID (Flitt Order ID)"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_orders',
        verbose_name="მომხმარებელი"
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_orders',
        verbose_name="არჩეული კურსი"
    )
    plan_type = models.CharField(
        max_length=20,
        choices=PlanType.choices,
        verbose_name="პაკეტის ტიპი"
    )
    amount_gel = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="თანხა (₾ GEL)"
    )
    amount_tetri = models.PositiveIntegerField(
        verbose_name="თანხა თეთრებში (Tetri)"
    )
    currency = models.CharField(
        max_length=3,
        default='GEL',
        verbose_name="ვალუტა"
    )
    order_desc = models.CharField(
        max_length=255,
        verbose_name="შეკვეთის აღწერა"
    )
    status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.CREATED,
        verbose_name="სტატუსი"
    )
    is_subscription = models.BooleanField(
        default=False,
        verbose_name="გამოწერაა (Subscription)"
    )
    flitt_payment_id = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="Flitt Payment ID"
    )
    masked_card = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name="დაფარული ბარათი"
    )
    card_type = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name="ბარათის ტიპი"
    )
    checkout_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Flitt Checkout URL"
    )
    payment_token = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Flitt Payment Token"
    )
    response_status = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name="Flitt Response Status"
    )
    response_code = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name="Flitt Response Code"
    )
    response_description = models.TextField(
        blank=True,
        default="",
        verbose_name="Flitt აღწერა"
    )
    raw_response = models.JSONField(
        blank=True,
        null=True,
        verbose_name="სრული Callback / Response JSON"
    )
    access_granted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="წვდომა მინიჭებულია",
        help_text="Set when course access was first granted from this payment.",
    )
    fulfilled_payment_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name="Fulfillment Payment ID",
        help_text="Flitt payment_id that last triggered access grant for this order.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="შექმნის თარიღი"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="განახლების თარიღი"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "გადახდის შეკვეთა"
        verbose_name_plural = "გადახდის შეკვეთები"

    def __str__(self):
        return f"{self.order_id} - {self.user} ({self.get_plan_type_display()}) [{self.status}]"

    @classmethod
    def generate_order_id(cls, prefix="MM"):
        unique_token = uuid.uuid4().hex[:12].upper()
        return f"{prefix}_{int(timezone.now().timestamp())}_{unique_token}"

    def fulfill_access_if_needed(
        self,
        *,
        rectoken="",
        subscription_order_id=None,
        payment_id=None,
    ):
        """
        Grant course access once per unique Flitt payment_id on this order.
        Returns True if access was granted/extended, False if already fulfilled.
        """
        pid = str(
            payment_id if payment_id is not None else (self.flitt_payment_id or "")
        )
        if self.access_granted_at:
            if not pid or self.fulfilled_payment_id == pid:
                return False
        if not self.course:
            return False

        UserCourseAccess.grant_or_renew_access(
            user=self.user,
            course=self.course,
            plan_type=self.plan_type,
            payment_order=self,
            rectoken=rectoken,
            subscription_order_id=subscription_order_id,
        )
        self.fulfilled_payment_id = pid
        if not self.access_granted_at:
            self.access_granted_at = timezone.now()
        self.save(update_fields=['fulfilled_payment_id', 'access_granted_at', 'updated_at'])
        return True


class UserCourseAccess(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_accesses',
        verbose_name="მომხმარებელი"
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='user_accesses',
        verbose_name="კურსი"
    )
    plan_type = models.CharField(
        max_length=20,
        choices=PlanType.choices,
        verbose_name="აქტიური პაკეტის ტიპი"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="აქტიურია"
    )
    auto_renew = models.BooleanField(
        default=True,
        verbose_name="ავტომატური განახლება"
    )
    starts_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="დაწყების თარიღი"
    )
    expires_at = models.DateTimeField(
        verbose_name="ვადის გასვლის თარიღი"
    )
    last_order = models.ForeignKey(
        PaymentOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name="ბოლო გადახდის შეკვეთა"
    )
    subscription_order_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
        db_index=True,
        verbose_name="Flitt გამოწერის ძირითადი შეკვეთის ID",
        help_text="Immutable root subscription order used for cancellation in Flitt.",
    )
    rectoken = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Flitt Recurring Token"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="შექმნის თარიღი"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="განახლების თარიღი"
    )

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = "კურსის წვდომა"
        verbose_name_plural = "კურსების წვდომები"

    def __str__(self):
        active_str = "აქტიური" if self.is_valid_now() else "ვადაგასული"
        return f"{self.user} - {self.course.title} ({self.get_plan_type_display()}) [{active_str}]"

    def is_valid_now(self):
        return self.is_active and self.expires_at > timezone.now()

    def get_subscription_order_id(self):
        """Root Flitt subscription order ID — required for stop/cancel after renewals."""
        if self.subscription_order_id:
            return self.subscription_order_id
        root = (
            PaymentOrder.objects.filter(
                user=self.user,
                course=self.course,
                is_subscription=True,
                status=OrderStatus.APPROVED,
            )
            .order_by('created_at')
            .values_list('order_id', flat=True)
            .first()
        )
        if root:
            return root
        if self.last_order:
            return self.last_order.order_id
        return None

    @classmethod
    def grant_or_renew_access(
        cls,
        user,
        course,
        plan_type,
        payment_order=None,
        rectoken="",
        subscription_order_id=None,
    ):
        now = timezone.now()
        duration_days = 30 if plan_type == PlanType.MONTHLY else 365

        access, created = cls.objects.get_or_create(
            user=user,
            course=course,
            defaults={
                'plan_type': plan_type,
                'is_active': True,
                'auto_renew': (plan_type == PlanType.MONTHLY),
                'starts_at': now,
                'expires_at': now + timedelta(days=duration_days),
                'last_order': payment_order,
                'subscription_order_id': subscription_order_id or "",
                'rectoken': rectoken or "",
            }
        )

        if not created:
            if access.is_valid_now():
                access.expires_at = access.expires_at + timedelta(days=duration_days)
            else:
                access.starts_at = now
                access.expires_at = now + timedelta(days=duration_days)

            access.plan_type = plan_type
            access.is_active = True
            if plan_type == PlanType.MONTHLY:
                access.auto_renew = True
            if payment_order:
                access.last_order = payment_order
            if subscription_order_id and not access.subscription_order_id:
                access.subscription_order_id = subscription_order_id
            if rectoken:
                access.rectoken = rectoken
            access.save()

        return access


