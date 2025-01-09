from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, LandLordProfile
import pdb
from celery import shared_task


@receiver(post_save, sender=User)
def send_account_notification(sender, instance, created, **kwargs):
    if created:  # Chỉ chạy khi user vừa được tạo
        user_name = instance.username
        user_role = instance.role
        user_email = instance.email

        if user_role == "tenant":
            message = f"Dear {user_name},\n\nYour Account has been created. You can now start using your account.\n\nThank you."
        elif user_role == "landlord":
            message = f"Dear {user_name},\n\nYour new account has been created but you cannot perform any operations because it is under review.\n\nThank you."
        else:
            return
        # Gửi email
        subject = "Your Account Status"
        send_mail(
            subject=subject,
            message=message,
            from_email="nodpou7@gmail.com",
            recipient_list=[user_email],
            fail_silently=False,
        )


@receiver(post_save, sender=LandLordProfile)
def send_approved_email(sender, instance, created, **kwargs):
    # Nếu không phải tạo mới và trạng thái approved đã thay đổi
    if not created:
        if instance.approved == True:  # Được phê duyệt
            subject = "Your Landlord Profile Status"
            message = f"Dear {instance.user.username},\n\nYour landlord profile has been approved. You can now start using your account to manage your properties.\n\nThank you."
        else:  # Bị từ chối
            subject = "Your Landlord Profile Status"
            message = f"Dear {instance.user.username},\n\nWe regret to inform you that your landlord profile has been rejected. Please contact our support team for further assistance.\n\nThank you."

        send_mail(
            subject,
            message,
            "nodpou7@gmail.com",  # From email
            [instance.user.email],  # To email
            fail_silently=False,
        )
