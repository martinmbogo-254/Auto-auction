# Generated by Django 5.0.7 on 2024-08-01 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0023_auction_current_time_alter_auction_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction',
            name='current_time',
        ),
    ]