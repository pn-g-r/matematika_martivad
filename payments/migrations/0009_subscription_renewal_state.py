from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('payments', '0008_paymentorder_subscription_canceled_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentorder',
            name='subscription_parent_order_id',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AddField(
            model_name='usercourseaccess',
            name='renewal_failed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
