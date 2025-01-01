from django.contrib import admin
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from codes.admin import admin_site

# hoc
from django.urls import path, re_path, include

schema_view = get_schema_view(
    openapi.Info(
        title="Course API",
        default_version="v1",
        description="APIs for CourseApp",
        contact=openapi.Contact(email="naot.ht@gmail.com"),
        license=openapi.License(name="Hoàng Trọng Toàn@2024"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path("", include("codes.urls")),
    path("admin/", admin_site.urls),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    # hoc này của outh2
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
]
