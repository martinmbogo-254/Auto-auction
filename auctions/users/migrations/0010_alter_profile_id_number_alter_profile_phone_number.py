# Generated by Django 5.0.6 on 2024-07-18 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_profile_id_number_profile_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='id_number',
            field=models.IntegerField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.IntegerField(blank=True, max_length=10, null=True),
        ),
    ]