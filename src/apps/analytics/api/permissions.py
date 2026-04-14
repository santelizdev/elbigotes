from rest_framework.permissions import BasePermission


class IsInternalUser(BasePermission):
    message = "Este endpoint está disponible solo para usuarios internos."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_internal_user", False)
        )
