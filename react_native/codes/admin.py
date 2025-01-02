from django.contrib import admin
from codes.models import (
    User,
    Follow,
    Comment,
    Notification,
    Post,
    LandLordProfile,
    # RoomOwner,
    Location,
    Image,
)

# hoc
from django.utils.html import mark_safe
from django.urls import path
from django.db.models import Count, Q
from datetime import datetime
from django.template.response import TemplateResponse


class MyAppAdmin(admin.AdminSite):
    site_header = "My App Admin"
    site_title = "My App Admin Portal"
    index_title = "Welcome to My App Admin Portal"

    def get_urls(self):
        return [path("stats/", self.stats)] + super().get_urls()

    def stats(self, request):
        from_date = request.GET.get("from_date", None)
        to_date = request.GET.get("to_date", None)
        users = User.objects.all()

        # Lọc theo khoảng thời gian
        if from_date:
            users = users.filter(
                date_joined__gte=datetime.strptime(from_date, "%Y-%m-%d")
            )
        if to_date:
            users = users.filter(
                date_joined__lte=datetime.strptime(to_date, "%Y-%m-%d")
            )

        # Thống kê
        statistics = users.values("role").annotate(count=Count("id"))

        stats = {
            "statistics": statistics,
            "from_date": from_date,
            "to_date": to_date,
        }
        return TemplateResponse(request, "admin/stats.html", {"stats": stats})


class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "role", "is_active", "display_avatar"]
    readonly_fields = ["display_avatar"]

    def display_avatar(self, obj):
        return mark_safe(
            f'<img src="{obj.avatar.url}" width="100" height="100" style="border-radius: 50%;" />'
        )

    display_avatar.short_description = "Avatar"


class LocationAdmin(admin.ModelAdmin):
    list_display = ("street", "ward", "district", "city", "latitude", "longitude")

    def maps_link(self, obj):
        if obj.google_maps_url():
            return format_html(
                f'<a href="{obj.google_maps_url()}" target="_blank">View on Map</a>'
            )
        return "No Coordinates"

    maps_link.short_description = "Google Maps Link"


class ImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "display_image",
    )
    readonly_fields = ["display_image"]

    def display_image(self, obj):
        return mark_safe(
            f'<img src="{obj.image.url}" width="100" height="100" style="border-radius: 50%;" />'
        )

    display_image.short_description = "Image"


class LandlordProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "approved", "location")
    list_filter = ("approved",)
    actions = ["approve_landlord"]

    def approve_landlord(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected landlords have been approved.")

    approve_landlord.short_description = "Approve selected landlords"


admin_site = MyAppAdmin()
admin_site.register(User, UserAdmin)
admin_site.register(Follow)
admin_site.register(Comment)
admin_site.register(Notification)
admin_site.register(Post)
admin_site.register(LandLordProfile, LandlordProfileAdmin)
admin_site.register(Location, LocationAdmin)
admin_site.register(Image, ImageAdmin)
