# Generated by Django 4.2.7 on 2023-12-27 17:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userbankaccount',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserAddress',
        ),
        migrations.DeleteModel(
            name='UserBankAccount',
        ),
    ]
