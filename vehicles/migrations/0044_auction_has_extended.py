# Generated by Django 5.0.7 on 2025-01-13 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0043_auction_approved_at_auction_approved_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='has_extended',
            field=models.BooleanField(default=False),
        ),
    ]
