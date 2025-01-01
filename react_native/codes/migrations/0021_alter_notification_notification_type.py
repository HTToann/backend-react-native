# Generated by Django 5.1.4 on 2025-01-01 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codes', '0020_alter_landlordprofile_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('comment_reply', 'Phản hồi bình luận'), ('new_post', 'Bài viết mới từ người theo dõi'), ('comment', 'Bình luận')], default=True, max_length=20),
        ),
    ]