from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.urls import reverse, NoReverseMatch
from django.core.validators import EmailValidator
import pdb

# hoc
from cloudinary.models import CloudinaryField

# hoc
from django.contrib.auth.models import AbstractUser


class Location(models.Model):
    street = models.CharField(max_length=50, null=True, blank=True)
    ward = models.CharField(max_length=50, null=True, blank=True)
    district = models.CharField(max_length=50, db_index=True)
    city = models.CharField(max_length=50, db_index=True)
    latitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
    )

    class Meta:
        unique_together = (
            "street",
            "ward",
            "district",
            "city",
        )  # Ràng buộc tính duy nhất

    def google_maps_url(self):
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
        return None

    def __str__(self):
        return f"{self.street or ''}, {self.ward or ''},{self.district},{self.city}"


class User(AbstractUser):
    ROLE_CHOICES = [
        ("landlord", "Chủ nhà trọ"),
        ("tenant", "Người thuê trọ"),
        ("admin", "Quản trị viên"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=True)
    avatar = CloudinaryField(
        "avatar",
        null=False,
        blank=True,
        default="https://res.cloudinary.com/dypt73wn0/image/upload/v1735226049/avatar-fb-mac-dinh-51nSxugr_mwqgny.jpg",
    )
    phone = models.CharField(
        max_length=30,
        null=False,
        blank=False,
        default=True,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Số điện thoại không hợp lệ.")],
    )
    email = models.EmailField(
        unique=False,
        null=False,  # Không cho phép giá trị NULL
        blank=False,  # Không cho phép để trống
        validators=[EmailValidator("Email không hợp lệ.")],  # Kiểm tra định dạng email
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_landlord(self):
        return self.role == "landlord"

    @property
    def is_tenant(self):
        return self.role == "tenant"

    @property
    def is_admin(self):
        return self.role == "admin"


class Image(models.Model):
    TYPE_CHOICES = [
        ("avatar", "Ảnh đại diện"),
        ("post", "Ảnh bài đăng"),
        # ảnh đăng ký chủ nhà trọ
        ("banner", "Ảnh banner"),
        ("room", "Ảnh phòng"),
    ]
    image_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=True)
    image = CloudinaryField("image")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} ({self.image_type})"


class LandLordProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="landlord_profile"
    )
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="landlord_profiles"
    )
    images = models.ManyToManyField("Image", related_name="landlord_profiles")
    # approved = models.BooleanField(default=False)
    approved = models.BooleanField()

    def __str__(self):
        return f"Landlord Profile of {self.user.username}"


class AbstractPost(models.Model):
    content = models.TextField()
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    people = models.PositiveIntegerField(default=1)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_date"]


class Post(AbstractPost):
    POST_TYPE_CHOICES = [
        ("rent", "Cho Thuê"),
        ("find", "Tìm Phòng"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="posts"
    )
    images = models.ManyToManyField("Image", related_name="posts", blank=True)
    type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.content[:50]}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(blank=False, null=False)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )  # Liên kết đến chính nó để hỗ trợ phản hồi
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_date"]  # Bình luận mới nhất hiển thị trước

    def __str__(self):
        return f"{self.user.username} - {self.content[:50]}"


class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followed"
    )
    followed_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "followed")

    def save(self, *args, **kwargs):
        if self.follower == self.followed:
            raise ValueError("Người dùng không thể tự theo dõi chính mình.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.follower.username} theo dõi {self.followed.username}"


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ("comment_reply", "Phản hồi bình luận"),
        ("new_post", "Bài viết mới từ người theo dõi"),
        ("comment", "Bình luận"),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default=True
    )
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)
    # link = models.URLField(null=True, blank=True, verbose_name="Liên kết")

    # Liên kết tới đối tượng bất kỳ (Comment, Post, ...)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return f"Thông báo cho {self.user.username} : {self.message[:50]}"
