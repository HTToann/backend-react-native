# Generated by Django 5.1.4 on 2024-12-28 05:33

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codes', '0006_comment_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image_type',
            field=models.CharField(choices=[('avatar', 'Ảnh đại diện'), ('post', 'Ảnh bài đăng'), ('banner', 'Ảnh banner')], default=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('comment_reply', 'Phản hồi bình luận'), ('new_post', 'Bài viết mới từ người theo dõi')], default=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='post',
            name='type',
            field=models.CharField(choices=[('rent', 'Cho Thuê'), ('find', 'Tìm Phòng')], default=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(default=True, max_length=30, validators=[django.core.validators.RegexValidator('^\\+?1?\\d{9,15}$', 'Số điện thoại không hợp lệ.')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('landlord', 'Chủ nhà trọ'), ('tenant', 'Người thuê trọ'), ('admin', 'Quản trị viên')], default=True, max_length=10),
        ),
        migrations.CreateModel(
            name='LandLordProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approved', models.BooleanField(default=False)),
                ('images', models.ManyToManyField(related_name='landlord_profiles', to='codes.image')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='landlord_profiles', to='codes.location')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='landlord_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
