# Generated by Django 5.0.7 on 2025-01-11 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0040_merge_0038_vehicle_is_hotsale_0039_vehicle_is_hotsale'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bidding',
            old_name='created_at',
            new_name='bid_time',
        ),
    ]
