# Generated by Django 5.0.7 on 2025-01-18 08:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0048_rename_is_dapproved_vehicle_is_disapproved'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='is_disapproved',
        ),
    ]
