# Generated by Django 5.0.7 on 2024-11-14 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0038_alter_vehicle_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='is_hotsale',
            field=models.BooleanField(default=False),
        ),
    ]
