# Generated by Django 5.1.4 on 2024-12-28 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codes', '0007_alter_image_image_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image_type',
            field=models.CharField(choices=[('avatar', 'Ảnh đại diện'), ('post', 'Ảnh bài đăng'), ('banner', 'Ảnh banner'), ('room', 'Ảnh phòng')], default=True, max_length=20),
        ),
    ]
