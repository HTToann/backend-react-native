from django.urls import path, include, re_path
from codes import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("users", views.UserViewSet, basename="user")
router.register(
    "landlord-profiles",
    views.ApproveLandlordProfileViewSet,
    basename="landlord-profile",
)
router.register(
    "pending-landlords", views.PendingLandlordListViewSet, basename="pending-landlord"
)
router.register("posts", views.PostViewSet, basename="post")
router.register("follows", views.FollowViewSet, basename="follow")
router.register("notifications", views.NotificationViewSet, basename="notification")
router.register("comment_detail", views.CommentDetailViewSet, basename="comment_detail")
router.register("post_detail", views.PostDetailViewSet, basename="post_detail")
router.register("post_search", views.PostSearchViewSet, basename="post_search")
# hoc
urlpatterns = [
    path("", include(router.urls)),
]
