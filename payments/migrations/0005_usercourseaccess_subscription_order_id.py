from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_delete_usersubscriptionaccess'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercourseaccess',
            name='subscription_order_id',
            field=models.CharField(
                blank=True,
                db_index=True,
                default='',
                help_text='Immutable root subscription order used for cancellation in Flitt.',
                max_length=64,
                verbose_name='Flitt გამოწერის ძირითადი შეკვეთის ID',
            ),
        ),
    ]
