# Generated by Django 5.1.4 on 2024-12-29 03:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codes', '0017_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, validators=[django.core.validators.EmailValidator('Email không hợp lệ.')]),
        ),
    ]
