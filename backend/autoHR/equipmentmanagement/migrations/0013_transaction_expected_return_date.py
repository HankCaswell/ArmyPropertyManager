# Generated by Django 5.0.4 on 2024-04-18 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipmentmanagement', '0012_alter_transaction_checkout_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='expected_return_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]