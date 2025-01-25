from argparse import Action
from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from codes import serializers
from codes.models import (
    User,
    LandLordProfile,
    Post,
    Location,
    Comment,
    Follow,
    Notification,
)
from codes import perm
from codes import pagination
from codes import apis
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
import pdb


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                response = super().create(request, *args, **kwargs)
                return response
            #     data = request.data
            #     user_name = data.get("username")
            #     user_role = data.get("role")
            #     user_email = data.get("email")
            #     # Gửi email thông báo
            #     subject = "Your Account Status"
            #     if user_role == "tenant":
            #         message = f"Dear {user_name},\n\nYour Account have created. You can now start using your account.\n\nThank you."
            #         send_mail(
            #             subject,
            #             message,
            #             "nodpou7@gmail.com",  # From email
            #             [user_email],  # To email
            #             fail_silently=False,
            #         )
            #         return Response(
            #             {"message": f"Account {user_name} has been created."},
            #             status=status.HTTP_201_CREATED,
            #         )
            #     if user_role == "landlord":
            #         message = f"Dear {user_name},\n\nYour new account has been created but you cannot perform any operations because it is under review.\n\nThank you."
            #         send_mail(
            #             subject,
            #             message,
            #             "nodpou7@gmaul.com",
            #             [user_email],
            #             fail_silently=False,
            #         )
            #         return Response(
            #             {"message": f"Account {user_name} has been created."},
            #             status=status.HTTP_201_CREATED,
            #         )
            # raise ValueError("Simulated error")
        except Exception as e:
            raise

    @action(
        methods=["get"],
        url_path="current-user",
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    # login
    def get_current_user(self, request):
        try:
            with transaction.atomic():
                user = request.user
                serializer = serializers.UserSerializer(user)
                return Response(serializer.data)
        except Exception as e:
            raise

    @action(
        methods=["post"],
        url_path="change-password",
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    # thay đổi mật khẩu
    def change_password(self, request):
        try:
            with transaction.atomic():
                user = request.user
                data = request.data
                old_password = data.get("old_password")
                new_password = data.get("new_password")
                confirm_password = data.get("confirm_password")
                if not old_password or not user.check_password(old_password):
                    return Response(
                        {"message": "Old Password is incorrect."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if new_password != confirm_password:
                    return Response(
                        {"message": "Passwords do not match."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if not new_password:
                    return Response(
                        {"message": "Password cannot be empty."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if len(new_password) < 6:
                    return Response(
                        {"message": "Password must be at least 6 characters long."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user.set_password(new_password)
                user.save()
                return Response({"Password has been changed."})
        except Exception as e:
            raise


# lấy danh sách tài khoản chưa được duyệt
class PendingLandlordListViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = LandLordProfile.objects.filter(approved=False)
    serializer_class = serializers.ApproveLandlordSerializer
    permission_classes = [IsAdminUser]  # Chỉ quản trị viên mới được phép truy cập


# sửa thuộc tính approved của LandLordProfile thành True ( QTV xét duyệt tài khoản)
class ApproveLandlordProfileViewSet(viewsets.ViewSet, generics.UpdateAPIView):
    queryset = LandLordProfile.objects.all()
    serializer_class = serializers.ApproveLandlordSerializer
    http_method_names = ["patch"]  # Chỉ cho phép PATCH
    permission_classes = [IsAdminUser]  # Chỉ quản trị viên mới được phép truy cập

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # nó sẽ lấy all objects từ queryset, get_object là lấy pk từ url
                instance = self.get_object()
                approved_status = request.data.get("approved", None)
                if approved_status is None:
                    return Response(
                        {"error": "Approved status is required."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Cập nhật trạng thái approved
                instance.approved = approved_status
                instance.save()
                if instance.approved == True:
                    status_text = "approved"
                else:
                    status_text = "rejected"
                return Response(
                    {
                        "message": f"Landlord {instance.user.username} has been {status_text}."
                    },
                    status=status.HTTP_200_OK,
                )
                # Gửi email thông báo
                # subject = "Your Landlord Profile Status"
                # if instance.approved:
                #     message = f"Dear {instance.user.username},\n\nYour landlord profile has been approved. You can now start using your account to manage your properties.\n\nThank you."
                # else:
                #     message = f"Dear {instance.user.username},\n\nWe regret to inform you that your landlord profile has been rejected. Please contact our support team for further assistance.\n\nThank you."

                # send_mail(
                #     subject,
                #     message,
                #     "nodpou7@gmail.com",  # From email
                #     [instance.user.email],  # To email
                #     fail_silently=False,
                # )

                # status_text = "approved" if instance.approved else "rejected"
                # return Response(
                #     {
                #         "message": f"Landlord {instance.user.username} has been {status_text}."
                #     },
                #     status=status.HTTP_200_OK,
                # )
            raise ValueError("Simulated error")
        except Exception as e:
            raise

    """Khi tạo bài đăng, 
    request.user không được serializer tự động truyền vào.
    Dữ liệu này không nằm trong payload mà client gửi, vì 
    vậy bạn cần chỉ định rõ user hiện tại bằng cách sử dụng serializer.save() với tham số user.
    Do không có filed user trong Post nên khi tạo post thì không có User cần phải truyền request.user ( user đang thực hiện apit này) vào filed
    user của post"""
    # permission_classes = [IsAuthenticated]


class PostViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    pagination_class = pagination.PostPagination

    def get_permissions(self):
        if self.action == "create":  # Tạo bài đăng
            if self.request.user.role == "tenant":
                return [permissions.IsAuthenticated()]
            elif self.request.user.role == "landlord":
                return [perm.IsApprovedLandlord()]
        elif self.action == "add_comments":  # Bình luận
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # nếu tạo post mà bị lỗi thì xóa chú thích ở dưới
        # validated_data = serializer.validated_data
        try:
            with transaction.atomic():
                user = self.request.user
                post = serializer.save(user=user)
                if user.role == "landlord":
                    followers = Follow.objects.filter(followed=user)
                    for follow in followers:
                        follower = follow.follower
                        send_mail(
                            subject="New Post Notification",
                            message=f"Dear {follower.username},\n\n{user.username} has a new posted!!",
                            from_email="nodpou7@gmail.com",
                            recipient_list=[follower.email],
                            fail_silently=False,
                        )
                        Notification.objects.create(
                            user=follow.follower,
                            message=f"{self.request.user.username} has a new posted!!:",
                            notification_type="new_post",
                            content_type=ContentType.objects.get_for_model(Post),
                            object_id=post.id,  # ID của bài viết vừa tạo
                        )
        except Exception as e:
            raise

    @action(methods=["get"], url_path="get_all_posts", detail=False)
    def get_all_post(self, request):
        try:
            with transaction.atomic():
                posts = Post.objects.all()
                serializer = serializers.PostSerializer(posts, many=True)
                return Response(serializer.data)
        except Exception as e:
            raise

    @action(
        methods=["post"],
        url_path="add-reply-comments",
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def add_comments(self, request, pk):
        try:
            with transaction.atomic():
                post = self.get_object()
                user = request.user
                content = request.data.get("content")
                parent_id = request.data.get("parent")
                if not content:
                    """này để frontend ràng buộc sẽ hay hơn, nếu comment là rỗng thì lock cái button đăng comment"""
                    return Response(
                        {"error": "Content is required for a comment."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                # Xử lý parent comment (nếu có)
                parent = None
                if parent_id:
                    try:
                        parent = Comment.objects.get(id=parent_id, post=post)
                    except Comment.DoesNotExist:
                        return Response(
                            {"error": "Parent comment not found."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                comment = Comment.objects.create(
                    user=user, post=post, content=content, parent=parent
                )
                Notification.objects.create(
                    user=post.user,
                    notification_type="comment",
                    message=f"You have comment on your post: {post.content[:50]}",
                    # content_object=comment,
                    content_object=post,  # Gắn bài viết thay vì comment
                )
                if parent:
                    Notification.objects.create(
                        user=parent.user,
                        notification_type="comment_reply",
                        message=f"{user.username} replied to your comment on: {post.content[:50]}",
                        # content_object=parent,
                        content_object=post,  # Gắn bài viết thay vì comment
                    )
                return Response(serializers.CommentSerializer(comment).data)
        except Exception as e:
            raise

    @action(methods=["get"], url_path="get-comments", detail=True)
    def get_comments(self, request, pk):
        try:
            with transaction.atomic():
                # để lấy các comment là root, nếu không có parent=none thì các comment là node cũng sẽ được hiển thị cùng cấp với cha
                comment = (
                    self.get_object()
                    .comments.select_related("user")
                    .filter(parent=None)
                )
                return Response(serializers.CommentSerializer(comment, many=True).data)
        except Exception as e:
            raise

    @action(methods=["get"], url_path="get-location", detail=True)
    def get_location(self, request, pk):
        try:
            with transaction.atomic():
                post = self.get_object()
                if post.type != "rent":
                    return Response(
                        {
                            "error": "Location is only available for posts with type 'rent'."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                address = f"{post.location.street},{post.location.ward},{post.location.district},{post.location.city}"
                latitude, longitude = apis.get_location_from_maps(address)
                if latitude and longitude:
                    url = f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}&travelmode=driving"
                    return Response(
                        {"message": "Location fetched successfully", "url": url},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Unable to fetch location from Google Maps"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["delete"], url_path="delete_post", detail=True)
    def delete_post(self, request, pk):
        try:
            with transaction.atomic():
                post = self.get_object()
                if post.user != request.user:
                    return Response(
                        {"Error": "You dont have permission to delete this post"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                post.delete()
                return Response(
                    {"Delete this post successfully"}, status=status.HTTP_204_NO_CONTENT
                )
        except:
            return Response(
                {"error": f"An error occurred: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["delete"], url_path="delete_comment", detail=True)
    def delete_comment(self, request, pk):
        try:
            with transaction.atomic():
                comment = Comment.objects.get(pk=pk)
                if comment.user != request.user:
                    return Response(
                        {"Error": "You dont have permission to delete this comment"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                comment.delete()
                return Response(
                    {"Delete this comment successfully"},
                    status=status.HTTP_204_NO_CONTENT,
                )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["delete"], url_path="delete_post", detail=True)
    def delete_post(self, request, pk):
        try:
            with transaction.atomic():
                post = self.get_object()
                if post.user != request.user:
                    return Response(
                        {"Error": "You dont have permission to delete this post"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                post.delete()
                return Response(
                    {"Delete this post successfully"}, status=status.HTTP_204_NO_CONTENT
                )
        except:
            return Response(
                {"error": f"An error occurred: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["delete"], url_path="delete_comment", detail=True)
    def delete_comment(self, request, pk):
        try:
            with transaction.atomic():
                comment = Comment.objects.get(pk=pk)
                if comment.user != request.user:
                    return Response(
                        {"Error": "You dont have permission to delete this comment"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                comment.delete()
                return Response(
                    {"Delete this comment successfully"},
                    status=status.HTTP_204_NO_CONTENT,
                )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    """lấy tất cả thông báo của user hiện tại
    thay vì truyền pk thì request.user sẽ nhanh hơn, vì request.user thể hiện
    của user ngay trên phía client đó"""

    @action(methods=["get"], detail=False, url_path="list")
    def list_notifications(self, request):
        try:
            with transaction.atomic():
                notifications = Notification.objects.filter(user=request.user)
                serializer = serializers.NotificationSerializer(
                    notifications, many=True
                )
                return Response(serializer.data)
        except Exception as e:
            raise

    """này dùng để đánh dấu thông báo đó đã đọc"""

    @action(methods=["post"], detail=True, url_path="mark-as-read")
    def mark_as_read(self, request, pk=None):
        try:
            with transaction.atomic():
                notification = get_object_or_404(Notification, pk=pk, user=request.user)
                notification.read_status = True
                notification.save()
                return Response({"message": "Notification marked as read."})
        except Exception as e:
            raise


class FollowViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=["post"], url_path="follow", detail=True)
    # pk = None để nếu không lấy giá trị được pk thì set cho là none
    def follow(self, request, pk=None):
        try:
            with transaction.atomic():
                follower = request.user
                followed = get_object_or_404(User, pk=pk, role="landlord")
                check = Follow.objects.filter(follower=follower, followed=followed)
                if follower.role != "tenant":
                    return Response(
                        {"message": "Only tenant just can follow landlord"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                if check.exists():
                    return Response(
                        {"message": "You are already following this landlord."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                Follow.objects.create(follower=request.user, followed=followed)
                return Response(
                    {"message": f"You are now following {followed.username}."},
                    status=status.HTTP_201_CREATED,
                )
        except Exception as e:
            raise

    @action(methods=["get"], url_path="is-following", detail=True)
    def is_following(self, request, pk=None):
        """
        Kiểm tra xem người dùng hiện tại có theo dõi landlord hay không.
        """
        follower = request.user
        followed = get_object_or_404(User, pk=pk, role="landlord")
        is_following = Follow.objects.filter(
            follower=follower, followed=followed
        ).exists()
        return Response({"is_following": is_following}, status=status.HTTP_200_OK)

    @action(methods=["delete"], url_path="unfollow", detail=True)
    def unfollow(self, request, pk=None):
        try:
            with transaction.atomic():
                follower = request.user
                followed = get_object_or_404(User, pk=pk, role="landlord")
                # kiểm tra xem có follow hay chưa
                follow = Follow.objects.filter(follower=follower, followed=followed)
                if not follow.exists():
                    return Response(
                        {"message": "You are not following this landlord."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                follow.delete()
                return Response(
                    {"message": f"You have unfollowed {followed.username}."},
                    status=status.HTTP_204_NO_CONTENT,
                )
        except Exception as e:
            raise


class PostSearchViewSet(viewsets.ViewSet):
    @action(methods=["get"], url_path="search", detail=False)
    def search(self, request):
        try:
            with transaction.atomic():
                street = request.query_params.get("street")
                ward = request.query_params.get("ward")
                district = request.query_params.get("district")
                city = request.query_params.get("city")
                min_price = request.query_params.get("min_price")
                max_price = request.query_params.get("max_price")
                people = request.query_params.get("people")
                posts = Post.objects.filter(type="rent")

                if street:
                    posts = posts.filter(location__street__icontains=street)
                if ward:
                    posts = posts.filter(location__ward__icontains=ward)
                if district:
                    posts = posts.filter(location__district__icontains=district)
                if city:
                    posts = posts.filter(location__city__icontains=city)

                if min_price:
                    posts = posts.filter(price__gte=min_price)
                if max_price:
                    posts = posts.filter(price__lte=max_price)
                if people:
                    posts = posts.filter(people__lte=people)
                serializer = serializers.PostSerializer(posts, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            raise


class CommentDetailViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentDetailSerializer


class PostDetailViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostDetailSerializer
