# Generated by Django 5.0.7 on 2024-08-26 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0031_alter_vehicle_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]