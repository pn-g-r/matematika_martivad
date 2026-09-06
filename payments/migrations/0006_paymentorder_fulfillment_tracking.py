from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0005_usercourseaccess_subscription_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentorder',
            name='access_granted_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Set when course access was first granted from this payment.',
                null=True,
                verbose_name='წვდომა მინიჭებულია',
            ),
        ),
        migrations.AddField(
            model_name='paymentorder',
            name='fulfilled_payment_id',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Flitt payment_id that last triggered access grant for this order.',
                max_length=64,
                verbose_name='Fulfillment Payment ID',
            ),
        ),
    ]
