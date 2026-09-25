from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('payments', '0007_fulfilledpayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentorder',
            name='subscription_canceled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
