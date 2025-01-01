from rest_framework.permissions import BasePermission


class IsTenant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "tenant"


class IsApprovedLandlord(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "landlord"
            and hasattr(request.user, "landlord_profile")
            and request.user.landlord_profile.approved
        )


# class IsApprovedLandlord(BasePermission):
#     def has_permission(self, request, view):
#         if not request.user.is_authenticated:
#             return False
#         if request.user.role == "tenant":
#             return True
#         if request.user.role == "landlord":
#             return (
#                 hasattr(request.user, "landlord_profile")
#                 and request.user.landlord_profile.approved
#             )
