# Generated by Django 5.0.7 on 2024-08-12 09:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0028_vehicle_transmission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionhistory',
            name='auction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='auction_history', to='vehicles.auction'),
        ),
        migrations.AlterField(
            model_name='auctionhistory',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='auction_history', to='vehicles.vehicle'),
        ),
        migrations.AlterField(
            model_name='vehicleimage',
            name='image',
            field=models.FileField(default='images/default-vehicle.png', upload_to='vehicleimages/'),
        ),
    ]
