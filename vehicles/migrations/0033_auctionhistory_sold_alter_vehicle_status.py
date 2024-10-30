# Generated by Django 5.0.7 on 2024-10-17 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0032_vehicle_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='auctionhistory',
            name='sold',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='status',
            field=models.CharField(choices=[('idle', 'idle'), ('available', 'available'), ('on_auction', 'on_auction'), ('on_bid', 'on_bid'), ('sold', 'sold')], default='idle', max_length=10),
        ),
    ]