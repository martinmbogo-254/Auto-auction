# Generated by Django 5.0.6 on 2024-07-18 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_profile_id_number_alter_profile_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='id_number',
            field=models.IntegerField(default=1, max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.IntegerField(default=1, max_length=10),
            preserve_default=False,
        ),
    ]
