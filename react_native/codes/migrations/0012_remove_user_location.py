# Generated by Django 5.1.4 on 2024-12-28 08:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codes', '0011_user_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='location',
        ),
    ]