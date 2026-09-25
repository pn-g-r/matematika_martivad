from django.db import migrations, models
import django.db.models.deletion


def backfill_fulfilled_payments(apps, schema_editor):
    PaymentOrder = apps.get_model('payments', 'PaymentOrder')
    FulfilledPayment = apps.get_model('payments', 'FulfilledPayment')
    database = schema_editor.connection.alias
    records = (
        FulfilledPayment(order_id=order_id, payment_id=payment_id)
        for order_id, payment_id in PaymentOrder.objects.using(database)
        .exclude(access_granted_at__isnull=True)
        .exclude(fulfilled_payment_id='')
        .values_list('id', 'fulfilled_payment_id')
    )
    FulfilledPayment.objects.using(database).bulk_create(records, batch_size=500)


class Migration(migrations.Migration):
    dependencies = [
        ('payments', '0006_paymentorder_fulfillment_tracking'),
    ]

    operations = [
        migrations.CreateModel(
            name='FulfilledPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.CharField(max_length=64)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fulfilled_payments', to='payments.paymentorder')),
            ],
            options={'unique_together': {('order', 'payment_id')}},
        ),
        migrations.RunPython(backfill_fulfilled_payments, migrations.RunPython.noop),
    ]
