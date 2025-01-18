import cloudinary
from rest_framework import serializers
from asgiref.sync import async_to_sync
from codes.models import (
    User,
    Location,
    Image,
    LandLordProfile,
    Post,
    Comment,
    Follow,
    Notification,
)
from django.db import transaction
from django.urls import reverse, NoReverseMatch
from codes import helper

import pdb


class ApproveLandlordSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandLordProfile
        fields = ["id", "approved"]


class LandLordProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandLordProfile
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"

    extra_kwargs = {
        "latitude": {"required": False},
        "longitude": {"required": False},
    }


class UserSerializer(serializers.ModelSerializer):
    street = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ward = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    district = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    images = serializers.ListField(
        child=serializers.ImageField(), required=False, allow_empty=False, min_length=3
    )
    avatar = serializers.ImageField(
        required=True
    )  # Bắt buộc người dùng phải upload avatar

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "password",
            "email",
            "phone",
            "street",
            "ward",
            "district",
            "city",
            "images",
            "avatar",
            "role",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "avatar": {"required": True},
            "phone": {"required": True},
            "role": {"required": True},
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, data):
        if data.get("role") == "landlord":
            # Kiểm tra bắt buộc các trường location
            required_fields = ["street", "ward", "district", "city"]
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                raise serializers.ValidationError(
                    {"location": f"Missing fields: {', '.join(missing_fields)}"}
                )

            # Kiểm tra images
            images = data.get("images", [])
            if not isinstance(images, list) or len(images) < 3:
                raise serializers.ValidationError(
                    {"images": "At least 3 images are required for landlord."}
                )
        if len(data.get("password")) < 6:
            raise serializers.ValidationError(
                {"password": "Password must be at least 6 characters long."}
            )
        if len(data.get("username")) < 6:
            raise serializers.ValidationError(
                {"username": "Username must be at least 6 characters long."}
            )
        return data

    def create(self, validated_data):
        try:
            with transaction.atomic():  # Bắt đầu một giao dịch
                # Lỗi xảy ra ở đây sẽ rollback toàn bộ transaction
                data = validated_data.copy()
                location_data = {
                    "street": data.pop("street", ""),
                    "ward": data.pop("ward", ""),
                    "district": data.pop("district", ""),
                    "city": data.pop("city", ""),
                }
                images_data = data.pop("images", [])
                avatar_file = data.pop("avatar")  # Lấy ảnh avatar
                role = data.get("role")

                # Tải avatar lên Cloudinary
                avatar_upload = async_to_sync(helper.upload_images_to_cloudinary)(
                    [avatar_file], upload_preset="avatar_preset"
                )
                data["avatar"] = avatar_upload[0]
                # Băm password
                user = User(**data)
                user.set_password(user.password)
                user.save()
                image_urls = []
                if role == "landlord":
                    image_urls = async_to_sync(helper.upload_images_to_cloudinary)(
                        images_data, upload_preset="image_preset"
                    )
                    location = helper.create_or_get_location(location_data)
                    helper.create_landlord_profile(user, location, image_urls)

                return user  # Trả về user đã được tạo
        except Exception as e:
            raise


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "image"]


class PostSerializer(serializers.ModelSerializer):
    street = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ward = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    district = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    city = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), required=False, allow_empty=True
    )
    images = ImageSerializer(required=False, many=True)
    username = serializers.CharField(
        source="user.username", read_only=True
    )  # Thêm trường này

    class Meta:
        model = Post
        fields = [
            "id",
            "user",
            "username",
            "content",
            "price",
            "people",
            "created_date",
            "updated_date",
            "street",
            "ward",
            "district",
            "city",
            "uploaded_images",
            "images",
            "type",
        ]
        read_only_fields = ["id", "created_date", "updated_date", "user"]
        extra_kwargs = {
            "content": {"required": True},
            "people": {"required": False},
            "type": {"required": True},
        }

    def validate(self, data):
        street = data.get("street")
        ward = data.get("ward")
        post_type = data.get("type")
        images = data.get("uploaded_images", [])
        price = data.get("price")
        people = data.get("people")

        if post_type == "rent":  # Nếu bài đăng là "Cho Thuê"
            if not images:
                raise serializers.ValidationError(
                    {"images": "At least one image is required for rent posts."}
                )
            if not price or price <= 0:
                raise serializers.ValidationError(
                    {"price": "Price is required for rent posts."}
                )
            if not people or people <= 0:
                raise serializers.ValidationError(
                    {"people": "People is required for rent posts."}
                )
            if not street:
                raise serializers.ValidationError(
                    {"street": "street is required for rent posts."}
                )
            if not ward:
                raise serializers.ValidationError(
                    {"ward": "ward is required for rent posts."}
                )
        return data

    def create(self, validated_data):
        try:
            with transaction.atomic():
                data = validated_data.copy()
                location_data = {
                    "street": data.pop("street", ""),
                    "ward": data.pop("ward", ""),
                    "district": data.pop("district", ""),
                    "city": data.pop("city", ""),
                }

                # Tạo hoặc lấy Location
                location, _ = Location.objects.get_or_create(
                    **location_data, defaults={"latitude": None, "longitude": None}
                )

                # Xử lý Images
                images_data = data.pop("uploaded_images", [])
                post = Post.objects.create(location=location, **data)
                image_urls = async_to_sync(helper.create_images_type)(
                    images_data, upload_preset="image_preset"
                )
                images = []
                for url in image_urls:
                    image = Image.objects.create(image=url, image_type="post")
                    images.append(image)
                post.images.set(images)
                post.save()
                # images = helper.create_images_type(images_data, type="post")
                return post
        except Exception as e:
            raise serializers.ValidationError(f"Error creating post: {e}")

    """do model post không có các field street,ward,district,city nên khi deserialize từ database để hiển 
    thị frontend client thì sẽ bị null,do Post có field là location cơ,muốn hiển thị các field của Location
    lên client cùng với post thì to_representation
    """

    def to_representation(self, instance):
        try:
            with transaction.atomic():
                representation = super().to_representation(instance)

                # Lấy thông tin location từ instance
                if instance.location:
                    representation["street"] = instance.location.street
                    representation["ward"] = instance.location.ward
                    representation["district"] = instance.location.district
                    representation["city"] = instance.location.city
                else:
                    representation["street"] = None
                    representation["ward"] = None
                    representation["district"] = None
                    representation["city"] = None

            return representation
        except Exception as e:
            raise serializers.ValidationError(f"Error creating post: {e}")


class PostDetailSerializer(PostSerializer):
    class Meta:
        model = PostSerializer.Meta.model
        fields = PostSerializer.Meta.fields


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "content",
            "user",
            "username",
            "parent",
            "replies",
            "created_date",
        ]

    def validate(self, data):
        try:
            with transaction.atomic():
                # Kiểm tra xem nếu có parent, parent phải thuộc cùng một post
                parent = data.get("parent")
                post = data.get("post")
                if parent and parent.post != post:
                    raise serializers.ValidationError(
                        "Parent comment must belong to the same post."
                    )
                return data
        except Exception as e:
            raise serializers.ValidationError(f"Error creating comment: {e}")

    def get_replies(self, obj):
        try:
            with transaction.atomic():
                replies = Comment.objects.filter(parent=obj).order_by("-created_date")
                return CommentSerializer(replies, many=True).data
        except Exception as e:
            raise serializers.ValidationError(f"Error creating reply comment: {e}")


class CommentDetailSerializer(CommentSerializer):
    class Meta:
        model = CommentSerializer.Meta.model
        fields = CommentSerializer.Meta.fields


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        models = Follow
        fields = "__all__"
        read_only_fields = ["id", "followed_date"]


class NotificationSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "message",
            "content_type",
            "read_status",
            "url",
        ]

    def get_url(self, obj):
        try:
            with transaction.atomic():
                if (
                    obj.notification_type == "comment_reply"
                    or obj.notification_type == "comment"
                ):
                    return reverse(       
                        "comment_detail-detail", kwargs={"pk": obj.object_id}
                    )
                elif obj.notification_type == "new_post":
                    return reverse("post_detail-detail", kwargs={"pk": obj.object_id})
        except NoReverseMatch:
            return "#"  # Trả về URL mặc định nếu không tìm thấy
        return "#"
