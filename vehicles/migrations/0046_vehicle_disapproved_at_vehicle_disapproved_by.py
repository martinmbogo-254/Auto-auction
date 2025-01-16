# Generated by Django 5.0.7 on 2025-01-16 13:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0045_bidding_awarded_bidding_is_auction_bid_awardhistory'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='disapproved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='disapproved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='disapproved_vehicles', to=settings.AUTH_USER_MODEL),
        ),
    ]
