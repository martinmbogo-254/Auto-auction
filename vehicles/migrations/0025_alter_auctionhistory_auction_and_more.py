# Generated by Django 5.0.7 on 2024-08-02 04:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0024_remove_auction_current_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionhistory',
            name='auction',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='auction_history', to='vehicles.auction'),
        ),
        migrations.AlterField(
            model_name='auctionhistory',
            name='end_date',
            field=models.DateTimeField(editable=False),
        ),
        migrations.AlterField(
            model_name='auctionhistory',
            name='returned_to_available',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='auctionhistory',
            name='sold',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='auctionhistory',
            name='start_date',
            field=models.DateTimeField(editable=False),
        ),
        migrations.AlterField(
            model_name='auctionhistory',
            name='vehicle',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='auction_history', to='vehicles.vehicle'),
        ),
    ]
