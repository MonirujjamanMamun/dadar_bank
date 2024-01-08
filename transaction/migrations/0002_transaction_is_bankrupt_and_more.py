# Generated by Django 4.2.7 on 2023-12-31 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='is_bankrupt',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.IntegerField(choices=[(1, 'Deposite'), (2, 'Withdrawal'), (3, 'Loan'), (4, 'Loan Paid')], null=True),
        ),
    ]
